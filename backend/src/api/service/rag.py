import uuid
import fitz  # PyMuPDF
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer
from api.config.core import settings
from api.database.table_models import DocumentChunk, ChatMessage
import requests
import replicate
import os
logger = logging.getLogger(__name__)

# ==========================================================
# Embedding Model
# ==========================================================
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# ==========================================================
# PDF Extractors
# ==========================================================
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file on disk."""
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    logger.info("✅ PDF text extracted from file")
    return text


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """Extract text directly from uploaded PDF bytes (in memory)."""
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()
    logger.info("✅ PDF text extracted from bytes")
    return text


# ==========================================================
# Text Splitter
# ==========================================================
def chunk_text(text: str, chunk_size=1000, chunk_overlap=200) -> List[str]:
    """Split text into overlapping chunks for LLM context windows."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    logger.info(f"✅ Text split into {len(chunks)} chunks")
    return chunks


# ==========================================================
# Store Chunks in DB with Embeddings
# ==========================================================
async def store_chunks_in_db(chunks: List[str], document_id: uuid.UUID, db: AsyncSession):
    """Generate embeddings for chunks and save them to PostgreSQL (pgvector)."""
    embeddings = embedding_model.encode(chunks)

    for chunk, vector in zip(chunks, embeddings):
        db.add(DocumentChunk(
            document_id=document_id,
            content=chunk,
            embedding=vector.tolist()
        ))
    await db.commit()
    logger.info(f"Stored {len(chunks)} chunks in DB")


# ==========================================================
# Similarity Search
# ==========================================================
async def search_similar_chunks(query: str, db: AsyncSession, top_k=5) -> List[str]:
    """Retrieve the most relevant chunks using pgvector similarity."""
    query_embedding = embedding_model.encode([query])[0].tolist()
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    sql = text("""
        SELECT content
        FROM document_chunks
        ORDER BY embedding <-> (:query_embedding)::vector
        LIMIT :top_k
    """)

    result = await db.execute(sql, {"query_embedding": embedding_str, "top_k": top_k})
    rows = [row[0] for row in result]
    logger.info(f"Retrieved {len(rows)} relevant chunks")
    return rows


# ==========================================================
# Call Gemma 3 via Replicate
# ==========================================================

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

client = OpenAI(api_key=REPLICATE_API_TOKEN)
def ask_gemma3(question: str, context: str) -> dict:
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"

    try:
        input = {"prompt": prompt}
        output = replicate.run(
            "google-deepmind/gemma-3-27b-it",
            input=input
        )

        if output:
            return {"answer": output, "raw_response": output}
        return {"answer": "Sorry, I could not get an answer.", "raw_response": ''}
    except Exception as e:
        return {"answer": "Error contacting Gemma API.", "raw_response": str(e)}

    except Exception as e:
        logger.error(f" Request to Gemma API failed: {str(e)}")
        return {"answer": "Error contacting Gemma API.", "raw_response": str(e)}

# ==========================================================
# Full RAG Pipeline + Save Chat History
# ==========================================================
async def process_question(question: str, db: AsyncSession, document_id: uuid.UUID, user_id: uuid.UUID):
    """
    Retrieval-Augmented Generation pipeline:
    1. Encode query into embeddings
    2. Search relevant document chunks from DB
    3. Send context + question to Gemma 3 via Replicate
    4. Save chat (question + answer) to DB
    5. Return response
    """
    chunks = await search_similar_chunks(question, db)
    context = "\n".join(chunks) if chunks else "No relevant content found in the document."

    logger.info(f"Context sent to Gemma (first 200 chars): {context[:200]}...")

    response = ask_gemma3(question, context)
    answer = response.get("answer", "No answer")

    #  Save chat history in DB
    user_msg = ChatMessage(user_id=user_id, document_id=document_id, role="user", message=question)
    assistant_msg = ChatMessage(user_id=user_id, document_id=document_id, role="assistant", message=answer)

    db.add_all([user_msg, assistant_msg])
    await db.commit()

    return {
        "question": question,
        "answer": answer,
        "raw_response": response.get("raw_response")
    }

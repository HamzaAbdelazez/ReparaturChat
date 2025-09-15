import uuid
import fitz  # PyMuPDF
import logging
import asyncio
import time
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer
from api.database.table_models import DocumentChunk, ChatMessage
import replicate
import os
from dotenv import load_dotenv

# ===================================
# Logging
# ===================================
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)  # suppress verbose polling logs

# Load environment variables
load_dotenv()

# ===================================
# Embedding Model
# ===================================
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ===================================
# PDF Extractors
# ===================================
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file path."""
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    logger.info("PDF text extracted from file")
    return text

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()
    logger.info(" PDF text extracted from bytes")
    return text

# =================================
# Text Splitter
# =================================
def chunk_text(text: str, chunk_size=800, chunk_overlap=200) -> List[str]:
    """Split long text into overlapping chunks for embedding/RAG."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    logger.info(f" Text split into {len(chunks)} chunks")
    return chunks

# ==========================================
# Store Chunks in DB with Embeddings
# ==========================================
async def store_chunks_in_db(chunks: List[str], document_id: uuid.UUID, db: AsyncSession):
    """Store text chunks + embeddings into DB."""
    embeddings = embedding_model.encode(chunks, batch_size=32, show_progress_bar=False)
    for chunk, vector in zip(chunks, embeddings):
        db.add(DocumentChunk(
            document_id=document_id,
            content=chunk,
            embedding=vector.tolist()
        ))
    await db.commit()
    logger.info(f" Stored {len(chunks)} chunks in DB")

# ==============================
# Similarity Search
# ==============================
async def search_similar_chunks(query: str, db: AsyncSession, document_id: uuid.UUID, top_k=5) -> List[str]:
    """Find most relevant chunks for a query inside a specific document."""
    query_embedding = embedding_model.encode([query])[0].tolist()
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    sql = text("""
        SELECT content
        FROM document_chunks
        WHERE document_id = :document_id
        ORDER BY embedding <-> (:query_embedding)::vector
        LIMIT :top_k
    """)

    result = await db.execute(
        sql, {"document_id": str(document_id), "query_embedding": embedding_str, "top_k": top_k}
    )
    rows = [row[0] for row in result]
    logger.info(f"🔍 Retrieved {len(rows)} relevant chunks")
    return rows

# ====================================
# Replicate API Setup
# ====================================
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise RuntimeError(" Missing REPLICATE_API_TOKEN. Please set it in your .env file or environment variables")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

#  Correct model slugs
GEMMA_MODEL_27B = "google-deepmind/gemma-3-27b-it:c0f0aebe8e578c15a7531e08a62cf01206f5870e9d0a67804b8152822db58c54"
GEMMA_MODEL_7B = "google-deepmind/gemma-3-7b-it"  # fallback model

# ====================================
# Replicate Helpers
# ====================================
def _normalize_replicate_output(output) -> str:
    """Normalize Replicate API output into a clean string."""
    if output is None:
        return ""
    if isinstance(output, str):
        return output.strip()
    if isinstance(output, (list, tuple)):
        return "".join(str(x) for x in output).strip()
    if isinstance(output, dict):
        return output.get("text", str(output))
    return str(output)

def _call_gemma(prompt: str, model_slug: str) -> str:
    """Run Gemma model on Replicate and normalize output."""
    output = replicate_client.run(model_slug, input={"prompt": prompt})
    return _normalize_replicate_output(output)

def ask_gemma3(question: str, context: str = "", stream: bool = False) -> dict:
    """Ask Gemma-3 a question with optional context. Falls back to smaller model if 27B fails."""
    MAX_CONTEXT_CHARS = 4000
    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS]

    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"

    try:
        if stream:
            answer_chunks = []
            for event in replicate.stream(GEMMA_MODEL_27B, input={"prompt": prompt}):
                if event.event == "output":
                    answer_chunks.append(str(event.data))
            answer_text = "".join(answer_chunks).strip()
            return {"answer": answer_text, "raw_response": answer_chunks}

        # Blocking mode with fallback
        try:
            answer_text = _call_gemma(prompt, GEMMA_MODEL_27B)
        except Exception as e:
            logger.warning(f"⚠️ Gemma-27B failed, retrying with 7B: {e}")
            answer_text = _call_gemma(prompt, GEMMA_MODEL_7B)

        if answer_text:
            return {"answer": answer_text.strip(), "raw_response": answer_text}

        return {"answer": "⚠️ Sorry, I could not get an answer.", "raw_response": ""}

    except Exception as e:
        logger.error(f"❌ Gemma API failed: {str(e)}")
        return {"answer": "⚠️ Error contacting Gemma API.", "raw_response": str(e)}

async def ask_gemma3_async(question: str, context: str = "", timeout: int = 500) -> dict:
    """Async wrapper with timeout + error handling."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(ask_gemma3, question, context),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error("⏳ Gemma API request timed out")
        return {"answer": "⚠️ Request timed out.", "raw_response": None}
    except Exception as e:
        logger.exception(f"❌ Unexpected error in ask_gemma3_async: {e}")
        return {"answer": "⚠️ Error contacting Gemma API.", "raw_response": str(e)}

# ===================================================
# Full RAG Pipeline + Save Chat History
# ===================================================
async def process_question(
    question: str,
    db: AsyncSession,
    document_id: uuid.UUID,
    user_id: uuid.UUID
):
    """RAG pipeline: search chunks → send to Gemma → save chat → return answer."""

    start_time = time.time()

    # Search chunks only for this document
    chunks = await search_similar_chunks(question, db, document_id=document_id)
    context = "\n".join(chunks) if chunks else "No relevant content found in the document."

    logger.info(f"📨 Context sent to Gemma (first 200 chars): {context[:200]}...")

    # Call Gemma with timeout
    try:
        response = await ask_gemma3_async(question, context, timeout=180)
    except asyncio.TimeoutError:
        logger.error("⚠️ Gemma request timed out")
        return {
            "question": question,
            "answer": "⚠️ Request timed out. Please try again.",
            "raw_response": None,
        }

    # Clean up the answer
    answer = response.get("answer", "⚠️ No answer")
    answer = answer.replace("<end_of_turn>", "").strip()
    raw_response = response.get("raw_response")

    # Save chat history
    user_msg = ChatMessage(
        user_id=user_id, document_id=document_id, role="user", message=question
    )
    assistant_msg = ChatMessage(
        user_id=user_id, document_id=document_id, role="assistant", message=answer
    )

    try:
        db.add_all([user_msg, assistant_msg])
        await db.commit()
        logger.info(" Chat messages saved")
    except Exception as e:
        logger.exception(f"❌ Failed to save chat messages: {e}")

    elapsed = time.time() - start_time
    logger.info(f"⏱️ Total time to get answer: {elapsed:.2f} seconds")

    return {
        "question": question,
        "answer": answer,
        "raw_response": raw_response,
        "elapsed_time": elapsed,
    }

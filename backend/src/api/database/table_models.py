import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import String, LargeBinary, DateTime, Integer, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector
from api.config.db import Base  # import Base from db.py


# ================= USERS =================
class User(Base):
    """Users table. Each user can upload multiple PDFs."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)

    # One-to-many: a user can upload multiple PDFs
    uploaded_pdfs: Mapped[List["UploadedPdf"]] = relationship(
        "UploadedPdf", back_populates="user", cascade="all, delete-orphan"
    )

    # One-to-many: a user can have many chat messages
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="user", cascade="all, delete-orphan"
    )


# ================= UPLOADED PDFs =================
class UploadedPdf(Base):
    """Table for uploaded PDFs. Stores binary content and metadata."""
    __tablename__ = "uploaded_pdfs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer)

    # Let Postgres set the timestamp automatically
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Foreign key to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="uploaded_pdfs")
    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="document", cascade="all, delete-orphan"
    )


# ================= DOCUMENT CHUNKS =================
class DocumentChunk(Base):
    """Extracted text chunks from PDFs with embeddings for semantic search."""
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploaded_pdfs.id", ondelete="CASCADE"),
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Embedding vector (example: MiniLM-L6-v2 with 384 dimensions)
    embedding: Mapped[List[float]] = mapped_column(Vector(384))

    # Relationship: chunk belongs to one PDF
    document: Mapped["UploadedPdf"] = relationship("UploadedPdf", back_populates="chunks")


# ================= CHAT MESSAGES =================
class ChatMessage(Base):
    """Chat messages table. Stores conversation history for each user."""
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploaded_pdfs.id", ondelete="CASCADE"),
        nullable=True
    )
    role: Mapped[str] = mapped_column(String(20))  # "user" or "assistant"
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # ✅ fix: use timezone.utc
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_messages")
    document: Mapped["UploadedPdf"] = relationship("UploadedPdf", back_populates="chat_messages")

import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import String, LargeBinary, DateTime, Integer, ForeignKey, Text, func, ARRAY , Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector
from api.config.db import Base  


# ================= USERS =================
class User(Base):
    """Users table. Each user can upload multiple PDFs."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    
    # Enhanced user profile fields for US31 (User Profile)
    skill_level: Mapped[int] = mapped_column(Integer, default=1)  # 1-5 scale
    physical_strength: Mapped[int] = mapped_column(Integer, default=3)  # 1-5 scale
    available_space: Mapped[int] = mapped_column(Integer, default=3)  # 1-5 scale (workspace size)
    experience_level: Mapped[int] = mapped_column(Integer, default=1)  # 1-5 scale
    
    # Profile completion date
    profile_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True
    )

    # One-to-many: a user can upload multiple PDFs
    uploaded_pdfs: Mapped[List["UploadedPdf"]] = relationship(
        "UploadedPdf", back_populates="user", cascade="all, delete-orphan"
    )

    # One-to-many: a user can have many chat messages
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="user", cascade="all, delete-orphan"
    )
    
    # One-to-many: a user can have multiple devices
    user_devices: Mapped[List["UserDevice"]] = relationship(
        "UserDevice", back_populates="user", cascade="all, delete-orphan"
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
    tools: Mapped[List["DocumentTool"]] = relationship(
    "DocumentTool", back_populates="document", cascade="all, delete-orphan"
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
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

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
    role: Mapped[str] = mapped_column(String(20)) 
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  
        nullable=False
    )

    # Add timestamp property for compatibility
    @property
    def timestamp(self):
        return self.created_at

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_messages")
    document: Mapped["UploadedPdf"] = relationship("UploadedPdf", back_populates="chat_messages")


# ================= DOCUMENT TOOLS & PARTS =================


class Tool(Base):
    """Tools table - stores info about tools, prices, and reusability."""
    __tablename__ = "tools"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(length=500), nullable=True)

    # lowest price in EUR (or another currency)
    min_price: Mapped[float] = mapped_column(Float, nullable=True)
    max_price: Mapped[float] = mapped_column(Float, nullable=True)

    
    reusability_score: Mapped[int] = mapped_column(Integer, nullable=True)  
    
    
    # tool category for organization
    category: Mapped[str] = mapped_column(String(length=100), nullable=True)
    
    
class DocumentTool(Base):
        # Mapping table between documents and required tools
        
        __tablename__ = "document_tools"
    
        id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        )
        document_id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True), ForeignKey("uploaded_pdfs.id", ondelete="CASCADE"), nullable=False
        )
        tool_id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True), ForeignKey("tools.id", ondelete="CASCADE"), nullable=False
        )
    
        # relationships
        document: Mapped["UploadedPdf"] = relationship("UploadedPdf", back_populates="tools")
        tool: Mapped["Tool"] = relationship("Tool")


# ================= DEVICES & MODELS =================
class Device(Base):
    """Device/Product models table."""
    __tablename__ = "devices"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    manufacturer: Mapped[str] = mapped_column(String(length=255), nullable=False)
    model: Mapped[str] = mapped_column(String(length=255), nullable=False)
    category: Mapped[str] = mapped_column(String(length=100), nullable=False)  # e.g., "washing machine"
    warranty_period_months: Mapped[int] = mapped_column(Integer, default=36)  # default 36 months
    repair_complexity: Mapped[int] = mapped_column(Integer, default=3)  
    
    # Relationships
    user_devices: Mapped[List["UserDevice"]] = relationship(
        "UserDevice", back_populates="device", cascade="all, delete-orphan"
    )


class UserDevice(Base):
    """User's owned devices with purchase information."""
    __tablename__ = "user_devices"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False
    )
    purchase_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    warranty_status: Mapped[str] = mapped_column(String(50), default="unknown")  # "active", "expired", "unknown"
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_devices")
    device: Mapped["Device"] = relationship("Device", back_populates="user_devices")


# ================= SERVICE PROVIDERS =================
class ServiceProvider(Base):
    __tablename__ = "service_providers"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    location: Mapped[str] = mapped_column(String(length=255), nullable=True)
    specialties: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    average_cost_per_hour: Mapped[float] = mapped_column(Float, nullable=True)
    average_repair_time_hours: Mapped[float] = mapped_column(Float, nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    commission_rate: Mapped[float] = mapped_column(Float, default=0.0)  # for US39
    website_url: Mapped[str] = mapped_column(String(length=500), nullable=True)  # for US41
    

# ================= TOOL PRICING =================
class ToolPrice(Base):
    __tablename__ = "tool_prices"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tools.id", ondelete="CASCADE"), nullable=False
    )
    vendor: Mapped[str] = mapped_column(String(length=255), nullable=False)  # "Amazon", "eBay", etc.
    price: Mapped[float] = mapped_column(Float, nullable=False)
    url: Mapped[str] = mapped_column(String(length=500), nullable=True)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationship
    tool: Mapped["Tool"] = relationship("Tool")



# ================= CONVERSATIONS =================
class Conversation(Base):
    """Conversations for organizing chat sessions with device context."""
    __tablename__ = "conversations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # Add device context to conversations
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    device: Mapped["Device"] = relationship("Device")  # Device context for conversation
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


# ================= MESSAGES =================
class Message(Base):
    """Individual messages within conversations."""
    __tablename__ = "messages"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(length=20), nullable=False)  # "user", "assistant", "pdf"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

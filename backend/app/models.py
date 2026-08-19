"""
AURA — SQLAlchemy ORM Models
Production relational schema supporting:
- PostgreSQL + pgvector (384-dim HNSW embeddings) & SQLite local fallback
- Memory entities, multimodal metadata, and provenance ledgers
- Explainable relationship graph with semantic evidence
- LangGraph agent checkpoints and state persistence
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import json

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Text, Boolean, ForeignKey, Index, LargeBinary
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from app.database import Base

try:
    from pgvector.sqlalchemy import Vector as PgVector
except ImportError:
    PgVector = None


class VectorType(TypeDecorator):
    """
    Dual-mode Vector type:
    - On PostgreSQL: maps to native pgvector `vector(dim)`
    - On SQLite/other: maps to `Text` (hex/JSON encoded float array)
    """
    impl = Text
    cache_ok = True

    def __init__(self, dim: int = 384, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and PgVector is not None:
            return dialect.type_descriptor(PgVector(self.dim))
        return dialect.type_descriptor(Text())


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=_uuid)
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=True)
    original_filename = Column(String, nullable=False)
    mime_type = Column(String, default="image/png")
    content_hash = Column(String, nullable=True, index=True)

    # OCR
    ocr_text = Column(Text, default="")       # cleaned
    ocr_raw = Column(Text, default="")        # raw output

    # Multimodal Vision-Language Understanding
    visual_summary = Column(Text, default="")
    visual_details = Column(Text, default="{}")       # JSON dict: layout, theme, color_palette, diagrams
    visual_objects = Column(Text, default="[]")       # JSON list of detected visual objects
    visual_entities = Column(Text, default="[]")      # JSON list of visual entities
    multimodal_provider = Column(String, default="gemini_vision")
    multimodal_status = Column(String, default="live_vision")  # live_vision | degraded_fallback
    provenance_ledger = Column(Text, default="[]")     # JSON list: [{"field": "...", "source": "VISION"|"OCR"|"DETERMINISTIC"|"INFERRED", "confidence": 0.95}]

    # General AI Understanding & Metadata
    summary = Column(Text, default="")
    category = Column(String, default="other", index=True)
    entities = Column(Text, default="[]")     # JSON list of strings
    topics = Column(Text, default="[]")       # JSON list of strings
    objects = Column(Text, default="[]")      # JSON list of strings
    
    # OS & Desktop Context
    application = Column(String, default="", index=True)
    window_title = Column(String, default="")
    source_type = Column(String, default="upload")  # "upload" | "desktop_capture" | "clipboard"
    clipboard_context = Column(Text, default="")    # Associated copied URL/text
    captured_at = Column(DateTime, nullable=True)

    document_type = Column(String, default="")
    important_information = Column(Text, default="[]")  # JSON

    # Scores
    importance_score = Column(Float, default=0.5)

    # Security
    sensitivity_level = Column(String, default="PUBLIC", index=True)  # PUBLIC/PERSONAL/SENSITIVE/CRITICAL
    sensitivity_findings = Column(Text, default="[]")     # JSON

    # Embedding: 384-dimensional dense representation (pgvector vector(384) in Postgres)
    embedding = Column(VectorType(384), nullable=True)

    # State
    processing_status = Column(String, default="pending", index=True)  # pending/processing/done/error
    processing_error = Column(Text, nullable=True)
    is_locked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    is_redacted = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=_now, index=True)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    # Composite Indexes
    __table_args__ = (
        Index("ix_memories_status_deleted", "processing_status", "is_deleted"),
        Index("ix_memories_cat_deleted", "category", "is_deleted"),
        Index("ix_memories_created_deleted", "created_at", "is_deleted"),
    )

    # Relationships
    source_relationships = relationship(
        "Relationship", foreign_keys="Relationship.source_memory_id",
        back_populates="source_memory", cascade="all, delete-orphan"
    )
    target_relationships = relationship(
        "Relationship", foreign_keys="Relationship.target_memory_id",
        back_populates="target_memory"
    )
    evidence_items = relationship("Evidence", back_populates="memory", cascade="all, delete-orphan")
    action_history = relationship("ActionHistory", back_populates="memory", cascade="all, delete-orphan")

    def get_entities(self) -> List[str]:
        try:
            return json.loads(self.entities or "[]")
        except Exception:
            return []

    def get_topics(self) -> List[str]:
        try:
            return json.loads(self.topics or "[]")
        except Exception:
            return []

    def get_objects(self) -> List[str]:
        try:
            return json.loads(self.objects or "[]")
        except Exception:
            return []

    def get_visual_details(self) -> Dict[str, Any]:
        try:
            return json.loads(self.visual_details or "{}")
        except Exception:
            return {}

    def get_visual_objects(self) -> List[str]:
        try:
            return json.loads(self.visual_objects or "[]")
        except Exception:
            return []

    def get_visual_entities(self) -> List[str]:
        try:
            return json.loads(self.visual_entities or "[]")
        except Exception:
            return []

    def get_provenance_ledger(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.provenance_ledger or "[]")
        except Exception:
            return []

    def get_sensitivity_findings(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.sensitivity_findings or "[]")
        except Exception:
            return []


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(String, primary_key=True, default=_uuid)
    source_memory_id = Column(String, ForeignKey("memories.id"), nullable=False, index=True)
    target_memory_id = Column(String, ForeignKey("memories.id"), nullable=False, index=True)
    relationship_type = Column(String, nullable=False, index=True)  # SAME_ENTITY, SAME_PROJECT, SAME_TOPIC, SEMANTICALLY_RELATED, TEMPORALLY_RELATED, DERIVED_FROM
    confidence = Column(Float, default=0.7)
    reason = Column(Text, default="")
    evidence = Column(Text, default="")
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    __table_args__ = (
        Index("ix_rel_src_tgt", "source_memory_id", "target_memory_id"),
    )

    source_memory = relationship("Memory", foreign_keys=[source_memory_id], back_populates="source_relationships")
    target_memory = relationship("Memory", foreign_keys=[target_memory_id], back_populates="target_relationships")


class Collection(Base):
    __tablename__ = "collections"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    type = Column(String, default="cluster")  # cluster/manual
    color = Column(String, default="#6366f1")
    created_at = Column(DateTime, default=_now)

    memberships = relationship("CollectionMemory", back_populates="collection", cascade="all, delete-orphan")


class CollectionMemory(Base):
    __tablename__ = "collection_memories"

    collection_id = Column(String, ForeignKey("collections.id"), primary_key=True)
    memory_id = Column(String, ForeignKey("memories.id"), primary_key=True)
    confidence = Column(Float, default=1.0)

    collection = relationship("Collection", back_populates="memberships")


class SearchSession(Base):
    __tablename__ = "search_sessions"

    id = Column(String, primary_key=True, default=_uuid)
    query = Column(Text, nullable=False)
    plan = Column(Text, default="[]")         # JSON execution trace
    result_ids = Column(Text, default="[]")   # JSON list of IDs
    confidence = Column(Float, default=0.0)
    mode = Column(String, default="search")   # search/investigate
    created_at = Column(DateTime, default=_now)


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=_uuid)
    memory_id = Column(String, ForeignKey("memories.id"), nullable=False, index=True)
    evidence_type = Column(String, nullable=False)  # ocr_match/entity_match/semantic/relationship/visual_match
    evidence_text = Column(Text, default="")
    confidence = Column(Float, default=0.7)
    created_at = Column(DateTime, default=_now)

    memory = relationship("Memory", back_populates="evidence_items")


class ActionHistory(Base):
    __tablename__ = "action_history"

    id = Column(String, primary_key=True, default=_uuid)
    memory_id = Column(String, ForeignKey("memories.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False)  # summarize/extract_expense/debug_code
    input_text = Column(Text, default="")
    output_text = Column(Text, default="")
    created_at = Column(DateTime, default=_now)

    memory = relationship("Memory", back_populates="action_history")


# ─── LangGraph State Persistence & Checkpointing ──────────────────────────────

class AgentCheckpoint(Base):
    """LangGraph State Checkpointer system of record."""
    __tablename__ = "agent_checkpoints"

    thread_id = Column(String, primary_key=True)
    checkpoint_ns = Column(String, primary_key=True, default="")
    checkpoint_id = Column(String, primary_key=True)
    parent_checkpoint_id = Column(String, nullable=True)
    type = Column(String, nullable=True)
    checkpoint = Column(Text, nullable=False)   # JSON / serialized state
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=_now)


class AgentCheckpointBlob(Base):
    """LangGraph Checkpoint channel blobs."""
    __tablename__ = "agent_checkpoint_blobs"

    thread_id = Column(String, primary_key=True)
    checkpoint_ns = Column(String, primary_key=True, default="")
    channel = Column(String, primary_key=True)
    version = Column(String, primary_key=True)
    type = Column(String, nullable=True)
    blob = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)


class AgentCheckpointWrite(Base):
    """LangGraph Checkpoint writes ledger."""
    __tablename__ = "agent_checkpoint_writes"

    thread_id = Column(String, primary_key=True)
    checkpoint_ns = Column(String, primary_key=True, default="")
    checkpoint_id = Column(String, primary_key=True)
    task_id = Column(String, primary_key=True)
    idx = Column(Integer, primary_key=True)
    channel = Column(String, nullable=False)
    type = Column(String, nullable=True)
    blob = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)


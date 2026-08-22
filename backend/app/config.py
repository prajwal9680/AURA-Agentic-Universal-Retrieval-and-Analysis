"""
AURA — Agentic Visual Memory Engine
Configuration: loads from backend/.env
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
THUMBNAILS_DIR = DATA_DIR / "thumbnails"
DB_PATH = DATA_DIR / "aura.db"


class Settings(BaseSettings):
    # Gemini API (optional — graceful local fallback if missing)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # OpenRouter API (high-throughput multimodal vision)
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemini-2.0-flash-001"

    # Multimodal Vision Provider ("auto", "gemini", "openrouter", "fallback")
    vision_provider: str = "auto"

    # App
    app_name: str = "AURA"
    debug: bool = False
    max_upload_size_mb: int = 50
    thumbnail_size: tuple = (400, 300)

    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Embedding model (local, no API key needed)
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Search weights
    weight_semantic: float = 0.45
    weight_text: float = 0.25
    weight_entity: float = 0.15
    weight_category: float = 0.10
    weight_temporal: float = 0.05

    # Relationship threshold
    relationship_threshold: float = 0.60

    # Database
    database_url: str = ""
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    use_pgvector: bool = True

    # Reranker & IR
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    rerank_candidate_pool: int = 40
    rerank_top_k: int = 15

    # Agentic RAG
    agent_max_iterations: int = 3
    agent_critic_threshold: float = 0.65

    # Rate Limiting & Production
    rate_limit_per_minute: int = 120

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

# Ensure data dirs exist at import time
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

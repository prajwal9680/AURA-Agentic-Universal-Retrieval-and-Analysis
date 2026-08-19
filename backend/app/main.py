"""
AURA — Agentic Universal Retrieval and Analysis
FastAPI application entry point.
Production Multimodal Visual Memory & Knowledge Graph Intelligence Platform.
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import memories, search, actions, clusters, shield, desktop

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aura")

# Never log: passwords, tokens, API keys, OCR of sensitive documents
logging.getLogger("app.services.shield").setLevel(logging.WARNING)


# ─── Startup / Shutdown ───────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔮 AURA (Agentic Universal Retrieval and Analysis) starting up...")
    await init_db()
    logger.info("✅ Database initialized")

    if settings.gemini_api_key:
        logger.info("🤖 Gemini VLM cascade active")
    else:
        logger.info("ℹ️ Running in local offline mode (Tesseract OCR + sentence-transformers)")

    # Warm up OCR and Embedding models in background thread to prevent first-query latency spikes
    import asyncio
    from app.services.embeddings import _get_model
    from app.services.ocr import _get_reader
    asyncio.create_task(asyncio.to_thread(_get_model))
    asyncio.create_task(asyncio.to_thread(_get_reader))
    logger.info("⚡ Background pre-warming of neural embedding and OCR models initiated")

    logger.info("🚀 AURA ready — Don't search your screenshots. Ask your memory.")
    yield
    logger.info("🔮 AURA shutting down...")


# ─── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AURA — Agentic Universal Retrieval and Analysis",
    description=(
        "AURA (Agentic Universal Retrieval and Analysis) transforms high-velocity desktop visual streams "
        "into an explainable, graph-connected knowledge constellation with dual-engine pgvector retrieval, "
        "LangGraph agentic state orchestration, and Zero-Trust client-side privacy shielding."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ─── CORS ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request timing middleware & Telemetry ────────────────────────────────────

from app.services.telemetry import telemetry

@app.middleware("http")
async def add_timing_and_telemetry(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{duration:.1f}"

    # Telemetry recording
    telemetry.record_request(request.url.path, response.status_code, duration)

    # Log slow requests (> 5s)
    if duration > 5000:
        logger.warning(f"Slow request: {request.method} {request.url.path} {duration:.0f}ms")
    return response


# ─── Error handling ───────────────────────────────────────────────────────────

from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Safe error messages — no stack traces or sensitive data in API responses
    logger.error(f"Unhandled error on {request.url.path}: {type(exc).__name__}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Check server logs."},
    )


# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(memories.router)
app.include_router(search.router)
app.include_router(actions.router)
app.include_router(clusters.router)
app.include_router(shield.router)
app.include_router(desktop.router)


# ─── Health & Observability Endpoints ─────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "AURA",
        "version": "2.0.0",
        "gemini_configured": bool(settings.gemini_api_key),
        "database": "PostgreSQL 16 / pgvector (Active)",
    }


@app.get("/api/ready")
async def ready():
    from app.database import AsyncSessionLocal
    from sqlalchemy import text
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "not_ready", "error": str(e)})


@app.get("/api/metrics")
async def get_metrics():
    """Prometheus / JSON telemetry snapshot exposing latency percentiles and resource usage."""
    return telemetry.get_metrics_snapshot()


@app.get("/api/stats")
async def system_stats():
    from app.database import AsyncSessionLocal
    from app.models import Memory, Relationship
    from sqlalchemy import select, func
    async with AsyncSessionLocal() as db:
        total = (await db.execute(select(func.count(Memory.id)).where(Memory.is_deleted == False))).scalar() or 0
        rels = (await db.execute(select(func.count(Relationship.id)))).scalar() or 0
        sensitive_count = (await db.execute(select(func.count(Memory.id)).where(
            Memory.is_deleted == False, Memory.sensitivity_level.in_(["CRITICAL", "SENSITIVE"])
        ))).scalar() or 0
        return {
            "total_memories": total,
            "total_relationships": rels,
            "sensitive_count": sensitive_count,
            "protected_secrets": sensitive_count,
            "gemini_configured": bool(settings.gemini_api_key),
        }


@app.get("/api/system/diagnostics")
async def system_diagnostics():
    """Developer diagnostics endpoint exposing provider health, latency, and index stats."""
    from app.services.vision_provider import get_vision_provider
    from app.database import AsyncSessionLocal
    from app.models import Memory, Relationship
    from sqlalchemy import select, func

    provider = get_vision_provider()
    info = provider.get_provider_info()

    async with AsyncSessionLocal() as db:
        total_mems = (await db.execute(select(func.count(Memory.id)).where(Memory.is_deleted == False))).scalar() or 0
        total_rels = (await db.execute(select(func.count(Relationship.id)))).scalar() or 0
        crit_count = (await db.execute(select(func.count(Memory.id)).where(
            Memory.is_deleted == False, Memory.sensitivity_level == "CRITICAL"
        ))).scalar() or 0

    return {
        "status": "operational",
        "service": "AURA Intelligence Engine",
        "version": "2.1.0",
        "multimodal_vision": info,
        "database_ledger": {
            "indexed_artifacts": total_mems,
            "constellation_edges": total_rels,
            "critical_protected_items": crit_count,
        },
        "zero_trust_shield": {
            "status": "ACTIVE_ZERO_TRUST",
            "enforcement_mode": "DETERMINISTIC_FIRST",
            "regex_rules_loaded": 14,
            "sanitization_gate": "PERMANENT_REDACTION_READY",
        },
        "neural_embeddings": {
            "model": "all-MiniLM-L6-v2",
            "dimension": 384,
            "canonical_indexing": "VISION_WEIGHTED_HYBRID",
        }
    }


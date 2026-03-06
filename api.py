"""
AgriBot — Production FastAPI Backend.

Provides REST API endpoints for the agentic RAG pipeline:
- POST /chat           — text-based query
- POST /chat/voice     — voice-based query (audio upload)
- POST /chat/image     — image-based query (photo upload)
- GET  /health         — system health check
- GET  /kg/stats       — knowledge graph statistics
- GET  /kg/search      — search KG entities

Designed for:
- React kiosk web UI (desktop/laptop)
- Mobile thin client over LAN/Wi‑Fi
"""

import sys
import tempfile
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

# --- Ensure project root is on path ---
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings
from agribot.logging_config import setup_logging, get_logger

setup_logging(json_output=True, log_level="INFO")
logger = get_logger("agribot.api")

# =============================================================================
# GLOBAL SERVICES (initialized at startup)
# =============================================================================
_services: dict = {}


def _init_services() -> dict:
    """Load all models and build the agent pipeline."""
    from agribot.llm.engine import get_llm
    from agribot.ingestion.index_builder import IndexBundle
    from agribot.retrieval.hybrid import HybridRetriever
    from agribot.retrieval.reranker import Reranker
    from agribot.knowledge_graph.schema import KnowledgeGraph
    from agribot.knowledge_graph.entity_linker import EntityLinker
    from agribot.knowledge_graph.seed_data import seed_knowledge_graph
    from agribot.agent.graph import build_agent_graph
    from agribot.translation.bangla_t5 import get_translator
    from agribot.voice.stt import get_stt
    from agribot.voice.tts import get_tts

    svc = {}

    # 1. LLM
    logger.info("Loading LLM model...")
    svc["llm"] = get_llm(
        model_path=str(settings.MODEL_PATH),
        n_ctx=settings.LLM_N_CTX,
        n_gpu_layers=settings.LLM_N_GPU_LAYERS,
    )

    # 2. Indexes
    logger.info("Loading document indexes...")
    if not settings.INDEX_DIR.exists():
        raise RuntimeError(
            f"Index directory not found: {settings.INDEX_DIR}. "
            "Run `python ingest.py` first."
        )
    svc["index_bundle"] = IndexBundle.load(settings.INDEX_DIR)

    # 3. Embedding model
    logger.info("Loading embedding model...")
    from sentence_transformers import SentenceTransformer
    svc["embedding_model"] = SentenceTransformer(settings.EMBEDDING_MODEL)

    # 4. Retriever
    svc["retriever"] = HybridRetriever(
        index_bundle=svc["index_bundle"],
        embedding_model=svc["embedding_model"],
        dense_top_k=settings.DENSE_TOP_K,
        sparse_top_k=settings.SPARSE_TOP_K,
        dense_weight=settings.DENSE_WEIGHT,
        sparse_weight=settings.SPARSE_WEIGHT,
    )

    # 5. Reranker
    logger.info("Loading reranker...")
    svc["reranker"] = Reranker(
        threshold=settings.RERANK_THRESHOLD,
        top_n=settings.RERANK_TOP_N,
    )

    # 6. Knowledge Graph
    logger.info("Loading knowledge graph...")
    svc["kg"] = KnowledgeGraph(settings.KG_DB_PATH)
    seed_knowledge_graph(svc["kg"])
    svc["entity_linker"] = EntityLinker(svc["kg"])

    # 7. Translator
    logger.info("Loading BanglaT5 translator...")
    svc["translator"] = get_translator(device="cpu")

    # 8. Voice services
    logger.info("Initializing voice services...")
    svc["stt"] = get_stt(model_size=settings.WHISPER_MODEL_SIZE)
    svc["tts"] = get_tts(rate=settings.TTS_RATE, bengali_voice_name=settings.TTS_BENGALI_VOICE)

    # 9. Agent graph
    logger.info("Building agent pipeline...")
    svc["agent"] = build_agent_graph(
        llm=svc["llm"],
        retriever=svc["retriever"],
        reranker=svc["reranker"],
        entity_linker=svc["entity_linker"],
        translator=svc["translator"],
        max_tokens=settings.LLM_MAX_TOKENS,
    )

    svc["kg_stats"] = svc["kg"].get_stats()
    svc["chunk_count"] = len(svc["index_bundle"].chunks)

    logger.info("All services initialized successfully")
    return svc


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle for FastAPI."""
    global _services
    logger.info("Starting AgriBot API server...")
    _services = _init_services()
    yield
    # Cleanup
    if "kg" in _services:
        _services["kg"].close()
    logger.info("AgriBot API server shutdown")


# =============================================================================
# APP
# =============================================================================
app = FastAPI(
    title="AgriBot API",
    description=(
        "Offline Multimodal Agentic RAG System for Bilingual "
        "(Bengali–English) Agricultural Decision Support"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React kiosk UI and mobile clients on local network
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to kiosk origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# MODELS
# =============================================================================

class ChatRequest(BaseModel):
    """Text-based chat request."""
    query: str = Field(..., min_length=1, max_length=2000, description="User query in English or Bengali")


class ChatResponse(BaseModel):
    """Chat response with bilingual answer and evidence."""
    answer: str = Field(..., description="English answer")
    answer_bn: str = Field(default="", description="Bengali translation")
    citations: list[str] = Field(default_factory=list, description="Source citations")
    kg_entities: list[dict] = Field(default_factory=list, description="Linked KG entities")
    evidence_grade: str = Field(default="N/A", description="Evidence quality grade")
    is_verified: bool = Field(default=False, description="Whether answer passed verification")
    verification_reason: str = Field(default="", description="Verification details")
    retry_count: int = Field(default=0, description="Number of retrieval retries")
    input_mode: str = Field(default="text", description="Input mode used")


class HealthResponse(BaseModel):
    """System health status."""
    status: str
    chunk_count: int
    kg_entities: int
    kg_aliases: int
    kg_relations: int


class KGSearchResponse(BaseModel):
    """Knowledge graph search results."""
    entities: list[dict]


# =============================================================================
# HELPER
# =============================================================================

def _build_initial_state(query: str, input_mode: str = "text") -> dict:
    """Build the initial agent state for a query."""
    return {
        "query_original": query,
        "query_language": "",
        "query_normalized": "",
        "query_expanded": "",
        "kg_entities": [],
        "evidences": [],
        "evidence_texts": "",
        "evidence_grade": "",
        "answer": "",
        "answer_bn": "",
        "citations": [],
        "is_verified": False,
        "verification_reason": "",
        "retry_count": 0,
        "should_refuse": False,
        "input_mode": input_mode,
        "input_audio_path": "",
        "error": "",
    }


def _run_agent(query: str, input_mode: str = "text") -> ChatResponse:
    """Run the agent pipeline and return a structured response."""
    agent = _services["agent"]
    initial_state = _build_initial_state(query, input_mode)

    try:
        result = agent.invoke(initial_state)
        return ChatResponse(
            answer=result.get("answer", "An error occurred."),
            answer_bn=result.get("answer_bn", ""),
            citations=result.get("citations", []),
            kg_entities=result.get("kg_entities", []),
            evidence_grade=result.get("evidence_grade", "N/A"),
            is_verified=result.get("is_verified", False),
            verification_reason=result.get("verification_reason", ""),
            retry_count=result.get("retry_count", 0),
            input_mode=input_mode,
        )
    except Exception as e:
        logger.error("Agent error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent processing error: {e}")


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health and KG statistics."""
    stats = _services.get("kg_stats", {})
    return HealthResponse(
        status="ok",
        chunk_count=_services.get("chunk_count", 0),
        kg_entities=stats.get("entities", 0),
        kg_aliases=stats.get("aliases", 0),
        kg_relations=stats.get("relations", 0),
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a text-based agricultural query.

    Accepts English or Bengali text. Returns bilingual answer
    with citations and evidence metadata.
    """
    logger.info("Chat query: %s", request.query[:100])
    return _run_agent(request.query, input_mode="text")


@app.post("/chat/voice", response_model=ChatResponse)
async def chat_voice(audio: UploadFile = File(..., description="Audio file (WAV/MP3)")):
    """
    Process a voice-based agricultural query.

    Accepts audio file upload, transcribes via Whisper ASR,
    then processes through the agent pipeline.
    """
    stt = _services["stt"]

    # Save uploaded audio to temp file
    suffix = Path(audio.filename).suffix if audio.filename else ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Transcribe
        result = stt.transcribe(tmp_path)
        query = result["text"]
        detected_lang = result["language"]
        logger.info("Voice transcription (%s): %s", detected_lang, query[:100])

        if not query.strip():
            raise HTTPException(status_code=400, detail="Could not transcribe audio")

        return _run_agent(query, input_mode="voice")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Voice processing error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Voice processing error: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.post("/chat/image", response_model=ChatResponse)
async def chat_image(
    image: UploadFile = File(..., description="Crop/plant photo (JPG/PNG)"),
    query: str = Form(default="", description="Optional text query to accompany the image"),
):
    """
    Process an image-based agricultural query.

    Accepts a crop/plant photo, generates a description using VLM,
    and processes through the agent pipeline.
    """
    # Save uploaded image to temp file
    suffix = Path(image.filename).suffix if image.filename else ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await image.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Process image through vision module
        from agribot.vision.image_processor import get_image_processor
        processor = get_image_processor()
        image_description = processor.describe_image(tmp_path)

        # Combine image description with optional text query
        if query.strip():
            combined_query = f"{query}\n\nImage analysis: {image_description}"
        else:
            combined_query = f"Based on this crop image: {image_description}"

        logger.info("Image query: %s", combined_query[:100])
        return _run_agent(combined_query, input_mode="image")

    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Image processing module not available. Install required dependencies.",
        )
    except Exception as e:
        logger.error("Image processing error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image processing error: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.get("/kg/stats")
async def kg_stats():
    """Get knowledge graph statistics."""
    kg = _services["kg"]
    return kg.get_stats()


@app.get("/kg/search", response_model=KGSearchResponse)
async def kg_search(q: str):
    """Search the knowledge graph for entities matching a term."""
    kg = _services["kg"]
    entities = kg.find_by_partial_alias(q)
    return KGSearchResponse(
        entities=[
            {
                "id": e.id,
                "canonical_bn": e.canonical_bn,
                "canonical_en": e.canonical_en,
                "entity_type": e.entity_type,
                "aliases": [a.alias_text for a in kg.get_aliases(e.id)],
            }
            for e in entities[:20]
        ]
    )


# =============================================================================
# TTS ENDPOINT
# =============================================================================

class TTSRequest(BaseModel):
    """Text-to-speech request."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    language: str = Field(default="en", description="Language: 'en' or 'bn'")


@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Synthesize text to speech and return WAV audio.

    Returns audio/wav stream for playback in the React frontend.
    """
    tts = _services.get("tts")
    if not tts:
        raise HTTPException(status_code=503, detail="TTS service not available")

    try:
        audio_path = tts.save_audio_temp(request.text, language=request.language)
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise HTTPException(status_code=500, detail="TTS audio generation failed")

        def audio_stream():
            with open(audio_path, "rb") as f:
                yield from iter(lambda: f.read(8192), b"")
            audio_path.unlink(missing_ok=True)

        return StreamingResponse(
            audio_stream(),
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=tts_output.wav"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("TTS error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")


# =============================================================================
# STATIC FILES — Serve React production build
# =============================================================================

_FRONTEND_DIR = PROJECT_ROOT / "frontend" / "dist"

if _FRONTEND_DIR.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA catch-all: serve index.html for client-side routing."""
        file_path = _FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_FRONTEND_DIR / "index.html"))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )

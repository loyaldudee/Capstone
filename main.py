"""
Aegis Insurance Claims Intelligence Assistant
---------------------------------------------
Main Application Entry Point (FastAPI)
Architecture:
  - models.py   : SQLAlchemy ORM models
  - database.py : DB session & auto-seeding engine
  - schemas.py  : Pydantic DTOs & response schemas
  - routes.py   : APIRouter endpoints
  - main.py     : FastAPI server, lifespan, middleware & static mount
"""

from fastapi import HTTPException
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Path configuration
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database import init_db
from routes import router as api_router, get_vector_engine
from ingestion_routes import ingest_router
from chat_routes import chat_router

STATIC_DIR = os.path.join(ROOT_DIR, "task4_evaluation_and_ui", "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle manager."""
    print("\n[Aegis Startup] Verifying database schema and auto-seeding...")
    init_db()

    print("[Aegis Startup] Pre-warming ChromaDB vector retrieval engine...")
    try:
        get_vector_engine()
        print("[Aegis Startup] ChromaDB vector engine ready.")
    except Exception as e:
        print(f"[Aegis Startup Warning] Could not pre-warm vector engine: {e}")

    print("[Aegis Startup] Starting Kafka consumer worker thread...")
    try:
        from ingestion_routes import start_kafka_consumer
        start_kafka_consumer()
    except Exception as e:
        print(f"[Aegis Startup Warning] Could not start Kafka consumer: {e}")

    yield
    print("[Aegis Shutdown] Server shutting down cleanly.")


app = FastAPI(
    title="Aegis Insurance Claims Intelligence Assistant",
    description="Agentic Multi-Agent Forensic Investigation & Decision Support Platform.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Modular API Routers
app.include_router(api_router)
app.include_router(ingest_router)
app.include_router(chat_router)

# Mount Static Assets
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


# Dynamic fallback handler for any assets built by Vite
@app.get("/assets/{asset_name:path}", include_in_schema=False)
def serve_vite_asset(asset_name: str):
    target = os.path.join(STATIC_DIR, "assets", asset_name)
    if os.path.exists(target):
        return FileResponse(target)
    raise HTTPException(status_code=404, detail=f"Asset {asset_name} not found")


# Root Web Dashboard Entry Point
@app.get("/", summary="Aegis Interactive Web UI")
def serve_dashboard():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        content={"message": "Aegis Claims Intelligence API active. Web UI index.html not found."},
        status_code=200
    )


# Dedicated Kafka Ingestion Portal Entry Point
@app.get("/ingest", summary="Kafka Ingestion & Sanitation Portal UI")
def serve_ingest_portal():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        content={"message": "Web UI index.html not found."},
        status_code=404
    )


# Dedicated Semantic Vector Search Entry Point
@app.get("/search", summary="ChromaDB Semantic Vector Search UI")
def serve_search_portal():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        content={"message": "Web UI index.html not found."},
        status_code=404
    )


# Dedicated Adjuster AI Chatbot Entry Point
@app.get("/chat", summary="Adjuster AI Chatbot UI")
def serve_chat_portal():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        content={"message": "Web UI index.html not found."},
        status_code=404
    )



if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 65)
    print("  AEGIS INSURANCE CLAIMS INTELLIGENCE ASSISTANT (MICROSERVICE)")
    print("  Running locally on http://127.0.0.1:8000")
    print("=" * 65 + "\n")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

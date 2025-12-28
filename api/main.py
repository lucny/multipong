"""
main.py – FastAPI aplikace pro MULTIPONG REST API.

Spuštění:
    uvicorn api.main:app --reload --port 9000

API dokumentace:
    http://localhost:9000/docs (Swagger UI)
    http://localhost:9000/redoc (ReDoc)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from api.db import init_db
from api.routers import players, matches, stats

# Lifespan pro inicializaci DB (nahrazuje deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("✅ Databáze inicializována")
    yield


# Inicializace FastAPI aplikace
app = FastAPI(
    title="MULTIPONG Stats API",
    description="REST API pro hráče, zápasy a statistiky MULTIPONG hry.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware - umožní přístup z webových aplikací
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statické soubory pro lehký frontend (HTMX/Tailwind)
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# Zaregistrování routerů
app.include_router(players.router)
app.include_router(matches.router)
app.include_router(stats.router)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint s informacemi o API."""
    return {
        "name": "MULTIPONG Stats API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "players": "/players",
            "matches": "/matches",
            "stats": "/stats"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

"""
FastAPI hlavní aplikace pro MULTIPONG
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import players

app = FastAPI(
    title="MULTIPONG API",
    description="REST API pro statistiky a správu MULTIPONG hry",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrace routerů
app.include_router(players.router)


@app.get("/")
async def root():
    """Základní endpoint."""
    return {
        "message": "MULTIPONG API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

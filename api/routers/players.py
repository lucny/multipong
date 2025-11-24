"""
FastAPI router pro správu hráčů
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter(
    prefix="/players",
    tags=["players"]
)


class Player(BaseModel):
    """Model hráče."""
    id: Optional[int] = None
    nickname: str
    total_games: int = 0
    total_wins: int = 0
    total_losses: int = 0
    rating: int = 1000


# Dočasné úložiště (později nahradit databází)
players_db: List[Player] = []


@router.get("/", response_model=List[Player])
async def get_players():
    """Vrátí seznam všech hráčů."""
    return players_db


@router.get("/{player_id}", response_model=Player)
async def get_player(player_id: int):
    """Vrátí konkrétního hráče."""
    for player in players_db:
        if player.id == player_id:
            return player
    raise HTTPException(status_code=404, detail="Hráč nenalezen")


@router.post("/", response_model=Player)
async def create_player(player: Player):
    """Vytvoří nového hráče."""
    player.id = len(players_db) + 1
    players_db.append(player)
    return player


@router.delete("/{player_id}")
async def delete_player(player_id: int):
    """Smaže hráče."""
    for i, player in enumerate(players_db):
        if player.id == player_id:
            players_db.pop(i)
            return {"message": "Hráč smazán"}
    raise HTTPException(status_code=404, detail="Hráč nenalezen")

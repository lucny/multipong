"""
players.py – REST API router pro hráče.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api.db import get_db
from api import crud, models, schemas

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("/", response_model=List[schemas.Player])
def list_players(db: Session = Depends(get_db)):
    """
    Vrátí seznam všech hráčů.
    
    Returns:
        List[Player]: Seznam všech hráčů v databázi
    """
    players = crud.get_all_players(db)
    return players


@router.get("/{player_id}", response_model=schemas.Player)
def get_player_by_id(player_id: str, db: Session = Depends(get_db)):
    """
    Vrátí konkrétního hráče podle player_id.
    
    Args:
        player_id: Unikátní ID hráče (např. "A1")
    
    Returns:
        Player: Daný hráč nebo HTTP 404
    """
    player = crud.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Hráč {player_id} nenalezen")
    return player


@router.post("/", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    """
    Vytvoří nového hráče.
    
    Args:
        player: Údaje nového hráče
    
    Returns:
        Player: Vytvořený hráč
    """
    # Zkontrolujeme, že hráč s tímto ID už neexistuje
    existing = crud.get_player(db, player.player_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Hráč {player.player_id} již existuje")
    
    return crud.create_player(db, player.player_id, player.team, player.name)



@router.delete("/{player_id}")
async def delete_player(player_id: int):
    """Smaže hráče."""
    for i, player in enumerate(players_db):
        if player.id == player_id:
            players_db.pop(i)
            return {"message": "Hráč smazán"}
    raise HTTPException(status_code=404, detail="Hráč nenalezen")

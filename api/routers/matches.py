"""
matches.py – REST API router pro zápasy.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api.db import get_db
from api import crud, models, schemas

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/", response_model=List[schemas.Match])
def list_matches(db: Session = Depends(get_db), limit: int = 20):
    """
    Vrátí seznam posledních zápasů.
    
    Args:
        limit: Maximální počet zápasů (default 20)
    
    Returns:
        List[Match]: Seznam zápasů
    """
    matches = crud.get_all_matches(db, limit=limit)
    return matches


@router.get("/{match_id}", response_model=schemas.Match)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """
    Vrátí detail konkrétního zápasu.
    
    Args:
        match_id: ID zápasu
    
    Returns:
        Match: Detail zápasu včetně statistik všech hráčů
    """
    match = crud.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Zápas {match_id} nenalezen")
    return match

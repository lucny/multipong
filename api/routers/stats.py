"""
stats.py – REST API router pro statistiky a leaderboard.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List

from api.db import get_db
from api import crud, models, schemas

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/leaderboard", response_model=List[schemas.LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db), limit: int = 10):
    """
    Vrátí leaderboard hráčů seřazený podle vstřelených gólů.
    
    Args:
        limit: Maximální počet hráčů (default 10)
    
    Returns:
        List[LeaderboardEntry]: Seřazený seznam hráčů
    """
    leaderboard = crud.get_leaderboard(db, limit=limit)
    return leaderboard


@router.get("/player/{player_id}")
def get_player_stats(player_id: str, db: Session = Depends(get_db)):
    """
    Vrátí историю statistik konkrétního hráče.
    
    Args:
        player_id: Player ID (např. "A1")
    
    Returns:
        dict: Histortie a souhrné statistiky hráče
    """
    player = crud.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Hráč {player_id} nenalezen")
    
    stats_list = crud.get_player_stats(db, player_id)
    
    total_hits = sum(s.hits for s in stats_list) if stats_list else 0
    total_goals_scored = sum(s.goals_scored for s in stats_list) if stats_list else 0
    total_goals_received = sum(s.goals_received for s in stats_list) if stats_list else 0
    
    return {
        "player_id": player.player_id,
        "name": player.name or player.player_id,
        "team": player.team,
        "matches_played": len(stats_list),
        "total_hits": total_hits,
        "total_goals_scored": total_goals_scored,
        "total_goals_received": total_goals_received,
        "average_hits_per_match": total_hits / len(stats_list) if stats_list else 0
    }


@router.get("/team/{team}")
def get_team_stats(team: str, db: Session = Depends(get_db)):
    """
    Vrátí agregované statistiky týmu.
    
    Args:
        team: Tým ("A" nebo "B")
    
    Returns:
        dict: Statistiky týmu včetně počtu zápasů a skóre
    """
    if team not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="Tým musí být 'A' nebo 'B'")
    
    team_stats = crud.get_team_stats(db)
    
    return {
        "team": team,
        "stats": team_stats.get(f"team_{team}", {})
    }


@router.get("/summary", response_model=schemas.SummaryStats)
def get_summary(db: Session = Depends(get_db)):
    """
    Vrátí shrnutí databáze.
    
    Returns:
        SummaryStats: Počet zápasů, hráčů, gólů apod.
    """
    total_matches = db.query(models.Match).count()
    total_players = db.query(models.Player).count()
    
    total_goals = db.query(func.sum(models.PlayerStats.goals_scored)).scalar() or 0
    
    avg_goals = total_goals / total_matches if total_matches > 0 else 0.0
    
    return schemas.SummaryStats(
        total_matches=total_matches,
        total_players=total_players,
        total_goals=total_goals,
        average_goals_per_match=avg_goals
    )


@router.get("/best_defender")
def get_best_defender(db: Session = Depends(get_db)):
    """
    Vrátí hráče s nejméně obdrženými góly (best defender).
    
    Returns:
        dict: Hráč s nejmenším počtem obdržených gólů
    """
    # Agregujeme data pro každého hráče
    results = db.query(
        models.Player.player_id,
        models.Player.name,
        models.Player.team,
        func.sum(models.PlayerStats.goals_received).label("total_received")
    ).join(
        models.PlayerStats, models.Player.id == models.PlayerStats.player_id
    ).group_by(
        models.Player.id
    ).order_by(
        "total_received"  # ascending order = nejméně obdržených
    ).first()
    
    if not results:
        raise HTTPException(status_code=404, detail="Žádní hráči v databázi")
    
    return {
        "player_id": results[0],
        "name": results[1] or results[0],
        "team": results[2],
        "total_goals_received": results[3]
    }


@router.get("/hottest_scorer")
def get_hottest_scorer(db: Session = Depends(get_db)):
    """
    Vrátí hráče s nejvíce vstřelenými góly.
    
    Returns:
        dict: Hráč s největším počtem gólů
    """
    results = db.query(
        models.Player.player_id,
        models.Player.name,
        models.Player.team,
        func.sum(models.PlayerStats.goals_scored).label("total_scored")
    ).join(
        models.PlayerStats, models.Player.id == models.PlayerStats.player_id
    ).group_by(
        models.Player.id
    ).order_by(
        desc("total_scored")
    ).first()
    
    if not results:
        raise HTTPException(status_code=404, detail="Žádní hráči v databázi")
    
    return {
        "player_id": results[0],
        "name": results[1] or results[0],
        "team": results[2],
        "total_goals_scored": results[3]
    }

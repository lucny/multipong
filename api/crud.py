"""
crud.py – Create, Read, Update, Delete operace pro databázi MULTIPONG.

Poskytuje high-level funkce pro práci s hráči, zápasy a statistikami.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from api import models
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


# ==================== PLAYER OPERATIONS ====================

def create_player(db: Session, player_id: str, team: str, name: Optional[str] = None) -> models.Player:
    """
    Vytvoří nového hráče v databázi.
    
    Args:
        db: Databázová session
        player_id: Jedinečné ID hráče (např. "A1", "B2")
        team: Tým ("A" nebo "B")
        name: Volitelné jméno hráče
    
    Returns:
        Vytvořený Player objekt
    """
    db_player = models.Player(player_id=player_id, team=team, name=name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    logger.info(f"✅ Hráč vytvořen: {player_id}")
    return db_player


def get_player(db: Session, player_id: str) -> Optional[models.Player]:
    """Získá hráče podle player_id."""
    return db.query(models.Player).filter(models.Player.player_id == player_id).first()


def get_or_create_player(db: Session, player_id: str, team: str) -> models.Player:
    """Získá hráče nebo ho vytvoří, pokud neexistuje."""
    player = get_player(db, player_id)
    if not player:
        player = create_player(db, player_id, team)
    return player


def get_all_players(db: Session) -> List[models.Player]:
    """Vrátí všechny hráče."""
    return db.query(models.Player).all()


def delete_player(db: Session, player_id: str) -> bool:
    """Smaže hráče a jeho statistiku."""
    player = get_player(db, player_id)
    if player:
        db.delete(player)
        db.commit()
        return True
    return False


# ==================== MATCH OPERATIONS ====================

def create_match(
    db: Session,
    team_left_score: int,
    team_right_score: int,
    duration_seconds: int
) -> models.Match:
    """
    Vytvoří nový zápas v databázi.
    
    Args:
        db: Databázová session
        team_left_score: Skóre levého týmu
        team_right_score: Skóre pravého týmu
        duration_seconds: Doba trvání zápasu v sekundách
    
    Returns:
        Vytvořený Match objekt
    """
    match = models.Match(
        team_left_score=team_left_score,
        team_right_score=team_right_score,
        duration_seconds=duration_seconds
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    logger.info(f"✅ Zápas vytvořen: {team_left_score} - {team_right_score}")
    return match


def get_match(db: Session, match_id: int) -> Optional[models.Match]:
    """Získá zápas podle ID."""
    return db.query(models.Match).filter(models.Match.id == match_id).first()


def get_all_matches(db: Session, limit: int = None) -> List[models.Match]:
    """
    Vrátí všechny zápasy (od nejnějnějšího).
    
    Args:
        db: Databázová session
        limit: Maximální počet zápasů (None = bez limitu)
    
    Returns:
        Seznam zápasů
    """
    query = db.query(models.Match).order_by(desc(models.Match.timestamp))
    if limit:
        query = query.limit(limit)
    return query.all()


# ==================== PLAYER STATS OPERATIONS ====================

def add_player_stats(
    db: Session,
    match_id: int,
    player_id: str,
    hits: int,
    goals_scored: int,
    goals_received: int
) -> models.PlayerStats:
    """
    Přidá statistiku hráče za zápas.
    
    Args:
        db: Databázová session
        match_id: ID zápasu
        player_id: Player ID (např. "A1")
        hits: Počet zásahů
        goals_scored: Počet vstřelených gólů
        goals_received: Počet obdržených gólů
    
    Returns:
        Vytvořený PlayerStats objekt
    """
    # Najdeme hráče podle player_id
    player = get_player(db, player_id)
    if not player:
        logger.error(f"❌ Hráč {player_id} neexistuje v databázi")
        return None
    
    stats = models.PlayerStats(
        match_id=match_id,
        player_id=player.id,
        hits=hits,
        goals_scored=goals_scored,
        goals_received=goals_received
    )
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def get_player_stats(db: Session, player_id: str) -> List[models.PlayerStats]:
    """Vrátí všechny statistiky hráče."""
    player = get_player(db, player_id)
    if not player:
        return []
    return db.query(models.PlayerStats).filter(models.PlayerStats.player_id == player.id).all()


# ==================== ANALYTICS ====================

def get_leaderboard(db: Session, limit: int = 10) -> List[Dict]:
    """
    Vrátí leaderboard hráčů seřazený podle vstřelených gólů.
    
    Args:
        db: Databázová session
        limit: Maximální počet hráčů
    
    Returns:
        Seznam slovníků s info o hráčích a jejich statistice
    """
    # Agregujeme data pro každého hráče
    from sqlalchemy import func
    
    results = db.query(
        models.Player.player_id,
        models.Player.name,
        models.Player.team,
        func.count(models.PlayerStats.id).label("matches_played"),
        func.sum(models.PlayerStats.hits).label("total_hits"),
        func.sum(models.PlayerStats.goals_scored).label("total_goals_scored"),
        func.sum(models.PlayerStats.goals_received).label("total_goals_received")
    ).join(
        models.PlayerStats, models.Player.id == models.PlayerStats.player_id
    ).group_by(
        models.Player.id
    ).order_by(
        desc("total_goals_scored")
    ).limit(limit).all()
    
    return [
        {
            "player_id": r[0],
            "name": r[1] or r[0],
            "team": r[2],
            "matches_played": r[3],
            "total_hits": r[4],
            "total_goals_scored": r[5],
            "total_goals_received": r[6]
        }
        for r in results
    ]


def get_team_stats(db: Session) -> Dict:
    """
    Vrátí agregované statistiky obou týmů.
    
    Returns:
        Slovník s statistikou týmů A a B
    """
    from sqlalchemy import func
    
    team_a = db.query(
        func.count(models.Match.id).label("matches"),
        func.sum(models.Match.team_left_score).label("total_goals_scored"),
        func.sum(models.Match.team_right_score).label("total_goals_received")
    ).all()[0]
    
    team_b = db.query(
        func.count(models.Match.id).label("matches"),
        func.sum(models.Match.team_right_score).label("total_goals_scored"),
        func.sum(models.Match.team_left_score).label("total_goals_received")
    ).all()[0]
    
    return {
        "team_A": {
            "matches": team_a[0] or 0,
            "total_goals_scored": team_a[1] or 0,
            "total_goals_received": team_a[2] or 0
        },
        "team_B": {
            "matches": team_b[0] or 0,
            "total_goals_scored": team_b[1] or 0,
            "total_goals_received": team_b[2] or 0
        }
    }

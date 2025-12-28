"""
schemas.py – Pydantic schémata pro FastAPI.

Definují strukturu dat, která API vrací.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


# ==================== PLAYER SCHEMAS ====================

class PlayerBase(BaseModel):
    """Základní údaje hráče."""
    player_id: str
    name: Optional[str] = None
    team: str


class PlayerCreate(PlayerBase):
    """Schéma pro vytvoření hráče."""
    pass


class Player(PlayerBase):
    """Úplný schéma hráče (včetně ID z DB)."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# ==================== MATCH SCHEMAS ====================

class PlayerStatsBase(BaseModel):
    """Základní údaje o statistice hráče."""
    player_id: int
    hits: int
    goals_scored: int
    goals_received: int


class PlayerStatsResponse(PlayerStatsBase):
    """Úplné schéma statistik hráče."""
    id: int
    match_id: int

    model_config = ConfigDict(from_attributes=True)


class MatchBase(BaseModel):
    """Základní údaje o zápase."""
    team_left_score: int
    team_right_score: int
    duration_seconds: int


class MatchCreate(MatchBase):
    """Schéma pro vytvoření zápasu."""
    pass


class Match(MatchBase):
    """Úplné schéma zápasu s statistikami."""
    id: int
    timestamp: datetime
    stats: List[PlayerStatsResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==================== STATISTICS SCHEMAS ====================

class LeaderboardEntry(BaseModel):
    """Položka leaderboardu."""
    player_id: str
    name: Optional[str] = None
    team: str
    matches_played: int
    total_hits: Optional[int] = None
    total_goals_scored: Optional[int] = None
    total_goals_received: Optional[int] = None


class TeamStats(BaseModel):
    """Statistiky týmu."""
    matches: int
    total_goals_scored: int
    total_goals_received: int


class TeamStatsResponse(BaseModel):
    """Odpověď s statistikami obou týmů."""
    team_A: TeamStats
    team_B: TeamStats


class SummaryStats(BaseModel):
    """Shrnutí databáze."""
    total_matches: int
    total_players: int
    total_goals: int
    average_goals_per_match: float

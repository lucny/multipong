"""
models.py – SQLAlchemy ORM modely pro MULTIPONG.

Tabulky:
- Player: Jednotliví hráči (pálky A1, B2, atd.)
- Match: Odehrané zápasy
- PlayerStats: Statistiky jednotlivých hráčů v každém zápase
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from api.db import Base


class Player(Base):
    """Tabulka hráčů (pálek)."""
    
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String(10), unique=True, index=True)  # např. "A1", "B2"
    name = Column(String(100), nullable=True)  # Volitelné jméno hráče
    team = Column(String(1))  # "A" nebo "B"

    # Vztahy
    stats = relationship("PlayerStats", back_populates="player")

    def __repr__(self):
        return f"<Player {self.player_id} ({self.team})>"


class Match(Base):
    """Tabulka zápasů."""
    
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    team_left_score = Column(Integer)  # Skóre levého týmu
    team_right_score = Column(Integer)  # Skóre pravého týmu
    duration_seconds = Column(Integer)  # Doba trvání zápasu

    # Vztahy
    stats = relationship("PlayerStats", back_populates="match", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Match {self.id}: {self.team_left_score} - {self.team_right_score} ({self.duration_seconds}s)>"


class PlayerStats(Base):
    """Tabulka statistik jednotlivých hráčů v každém zápase."""
    
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), index=True)
    player_id = Column(Integer, ForeignKey("players.id"), index=True)
    
    hits = Column(Integer)  # Počet zásahů do míčku
    goals_scored = Column(Integer)  # Počet vstřelených gólů
    goals_received = Column(Integer)  # Počet obdržených gólů

    # Vztahy
    match = relationship("Match", back_populates="stats")
    player = relationship("Player", back_populates="stats")

    def __repr__(self):
        return f"<PlayerStats match={self.match_id} player_id={self.player_id}: {self.hits} hits>"

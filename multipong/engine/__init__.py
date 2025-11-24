"""
Herní engine pro MULTIPONG
Obsahuje: Ball, Paddle, Arena, MultipongEngine, PlayerStats, Team, GoalZone
Logické jádro hry - nezávislé na Pygame.
"""

from .ball import Ball
from .paddle import Paddle
from .arena import Arena
from .game_engine import MultipongEngine
from .player_stats import PlayerStats
from .team import Team
from .goal_zone import GoalZone

__version__ = "0.1.0"

__all__ = [
    "Ball",
    "Paddle", 
    "Arena",
    "MultipongEngine",
    "PlayerStats",
    "Team",
    "GoalZone",
]

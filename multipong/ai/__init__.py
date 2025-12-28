"""AI moduly pro MULTIPONG."""

from .base_ai import BaseAI
from .helpers import assign_ai_to_slots, assign_ai_to_team, clear_team_ai
from .predictive_ai import PredictiveAI
from .qlearning_ai import QLearningAI
from .simple_ai import SimpleAI
from .static_ai import StaticAI

__all__ = [
    "BaseAI",
    "StaticAI",
    "SimpleAI",
    "PredictiveAI",
    "QLearningAI",
    "assign_ai_to_team",
    "assign_ai_to_slots",
    "clear_team_ai",
]

__version__ = "0.3.0"
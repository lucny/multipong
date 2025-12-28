"""Helpers pro automatické přiřazení AI do týmů."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # typové importy pouze pro lint/IDE
    from multipong.engine import Team

from .predictive_ai import PredictiveAI
from .qlearning_ai import QLearningAI
from .simple_ai import SimpleAI
from .static_ai import StaticAI


def assign_ai_to_team(team: "Team", level: int = 1) -> None:
    """Přiřadí AI určité obtížnosti všem volným pálkám v týmu.

    Args:
        team: Instance týmu
        level: Obtížnost AI (0=statická, 1=simple, 2=predictive, 3=qlearning)
    """
    ai_class = _get_ai_class(level)

    for paddle in team.paddles:
        if paddle.ai is None:
            if level == 3:
                paddle.ai = ai_class(lr=0.1, gamma=0.9, epsilon=0.1)
            else:
                paddle.ai = ai_class()


def assign_ai_to_slots(
    team: "Team", slot_indices: list[int], level: int = 1
) -> None:
    """Přiřadí AI konkrétním slotům.

    Args:
        team: Instance týmu
        slot_indices: Indexy pálek k obsazení AI (0-3)
        level: Obtížnost AI
    """
    ai_class = _get_ai_class(level)

    for idx in slot_indices:
        if 0 <= idx < len(team.paddles):
            paddle = team.paddles[idx]
            if paddle.ai is None:
                if level == 3:
                    paddle.ai = ai_class(lr=0.1, gamma=0.9, epsilon=0.1)
                else:
                    paddle.ai = ai_class()


def clear_team_ai(team: "Team") -> None:
    """Odstraní všechny AI z týmu (pro případ, že se připojí hráči)."""
    for paddle in team.paddles:
        paddle.ai = None


def _get_ai_class(level: int):
    """Vrátí třídu AI podle úrovně."""
    if level == 0:
        return StaticAI
    elif level == 1:
        return SimpleAI
    elif level == 2:
        return PredictiveAI
    elif level == 3:
        return QLearningAI
    else:
        return SimpleAI  # fallback

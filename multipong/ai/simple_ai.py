"""Jednoduchá heuristická AI pro MULTIPONG."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

from .base_ai import Action, BaseAI

if TYPE_CHECKING:  # pouze pro typovou kontrolu, aby se zamezilo cyklům importů
    from multipong.engine import Arena, Ball, Paddle


class SimpleAI(BaseAI):
    """Sleduje vertikální pozici míčku a drží pálku u středu míčku."""

    def __init__(self, reaction_speed: float = 1.0, dead_zone: float = 5.0) -> None:
        self.reaction_speed = max(reaction_speed, 0.01)
        self.dead_zone = max(dead_zone, 0.0)

    def decide(self, paddle: "Paddle", ball: "Ball", arena: "Arena") -> Action:  # noqa: ARG002
        center = paddle.y + paddle.height / 2
        target_y = ball.y
        effective_dead_zone = self.dead_zone / self.reaction_speed

        if center > target_y + effective_dead_zone:
            return {"up": True, "down": False}
        if center < target_y - effective_dead_zone:
            return {"up": False, "down": True}
        return {"up": False, "down": False}

    # Kompatibilní alias pro původní API ("up"/"down"/"stay")
    def decide_action(self, paddle_y: float, ball_y: float, paddle_height: float) -> str:
        action = self.decide(
            SimpleNamespace(y=paddle_y, height=paddle_height),
            SimpleNamespace(y=ball_y),
            SimpleNamespace(),
        )

        if action.get("up"):
            return "up"
        if action.get("down"):
            return "down"
        return "stay"

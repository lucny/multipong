"""Prediktivní AI – odhadne budoucí pozici míčku.

Používá krátkou simulaci pohybu míčku a snaží se dorovnat pálku
na predikovanou Y souřadnici.
"""

from __future__ import annotations

import copy
import random
from typing import TYPE_CHECKING

from .base_ai import Action, BaseAI

if TYPE_CHECKING:  # typové importy pouze pro lint/IDE
    from multipong.engine import Arena, Ball, Paddle


class PredictiveAI(BaseAI):
    """Jednoduchý prediktivní agent s volitelným šumem."""

    def __init__(self, prediction_steps: int = 120, noise: float = 0.0) -> None:
        self.prediction_steps = max(1, int(prediction_steps))
        self.noise = max(0.0, float(noise))

    def decide(self, paddle: "Paddle", ball: "Ball", arena: "Arena") -> Action:
        sim_ball = copy.copy(ball)

        for _ in range(self.prediction_steps):
            self._step_ball(sim_ball, arena)

        target_y = sim_ball.y
        if self.noise:
            target_y += random.uniform(-self.noise, self.noise)

        center = paddle.y + paddle.height / 2
        return {"up": center > target_y, "down": center < target_y}

    @staticmethod
    def _step_ball(sim_ball: "Ball", arena: "Arena") -> None:
        """Simuluje jeden krok pohybu míčku s odrazem od stropu/podlahy."""
        sim_ball.x += sim_ball.vx
        sim_ball.y += sim_ball.vy

        if sim_ball.y - sim_ball.radius <= 0:
            sim_ball.y = sim_ball.radius
            sim_ball.vy = abs(sim_ball.vy)
        elif sim_ball.y + sim_ball.radius >= arena.height:
            sim_ball.y = arena.height - sim_ball.radius
            sim_ball.vy = -abs(sim_ball.vy)

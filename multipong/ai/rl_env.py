"""Zjednodušené RL prostředí pro trénování Q-learning agenta na Pongu."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class State:
    """Stav v RL prostředí."""

    ball_x: float
    ball_y: float
    ball_vx: float
    ball_vy: float
    paddle_y: float


class RLPongEnv:
    """
    Minimalistické RL prostředí pro Pong.

    - Jedna pálka vlevo, jeden míček.
    - Míček se pohybuje a odráží se od horní/dolní stěny.
    - Epizoda skončí, když míček proletí vlevo za pálkou.
    """

    def __init__(
        self,
        width: float = 400.0,
        height: float = 300.0,
        paddle_height: float = 60.0,
        paddle_speed: float = 5.0,
        ball_speed: float = 4.0,
        paddle_x: float = 10.0,
    ) -> None:
        self.width = float(width)
        self.height = float(height)
        self.paddle_height = float(paddle_height)
        self.paddle_speed = float(paddle_speed)
        self.ball_speed = float(ball_speed)
        self.paddle_x = float(paddle_x)

        self.reset()

    def reset(self) -> State:
        """Resetuje prostředí a vrátí počáteční stav."""
        self.ball_x = self.width / 2.0
        self.ball_y = self.height / 2.0
        self.ball_vx = self.ball_speed
        self.ball_vy = self.ball_speed
        self.paddle_y = self.height / 2.0 - self.paddle_height / 2.0

        return self._get_state()

    def step(self, action: int) -> tuple[State, float, bool]:
        """
        Vykoná jeden krok v prostředí.

        Args:
            action: 0=stay, 1=up, 2=down

        Returns:
            (next_state, reward, done)
        """
        # Pohyb pálky
        if action == 1:
            self.paddle_y -= self.paddle_speed
        elif action == 2:
            self.paddle_y += self.paddle_speed

        self.paddle_y = max(0.0, min(self.height - self.paddle_height, self.paddle_y))

        # Pohyb míčku
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        # Odraz od horní/dolní stěny
        if self.ball_y <= 0.0 or self.ball_y >= self.height:
            self.ball_vy *= -1.0
            self.ball_y = max(0.0, min(self.height, self.ball_y))

        reward = 0.0
        done = False

        # Kolize s pálkou (vlevo)
        if self.ball_x <= self.paddle_x + 10.0:
            if self.paddle_y <= self.ball_y <= self.paddle_y + self.paddle_height:
                # Zásah – míček se odrazí
                self.ball_vx = abs(self.ball_vx)
                reward = 1.0
            else:
                # Netrefil – konec epizody
                reward = -5.0
                done = True

        # Míček vpravo – jednoduchý odraz
        if self.ball_x >= self.width:
            self.ball_vx = -abs(self.ball_vx)

        return self._get_state(), reward, done

    def _get_state(self) -> State:
        """Vrátí aktuální stav."""
        return State(
            ball_x=self.ball_x,
            ball_y=self.ball_y,
            ball_vx=self.ball_vx,
            ball_vy=self.ball_vy,
            paddle_y=self.paddle_y,
        )

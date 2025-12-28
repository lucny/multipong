"""Q-learning AI agent pro MULTIPONG.

Udržuje Q tabulku ve tvaru ``Q[(state)][action]`` a používá epsilon-greedy
politiku pro výběr akce.
"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple, TYPE_CHECKING

from .base_ai import Action, BaseAI

if TYPE_CHECKING:  # typové importy pouze pro lint/IDE
    from multipong.engine import Arena, Ball, Paddle

State = Tuple[int, int, int]


class QLearningAI(BaseAI):
    """Jednoduchý Q-learning agent pro demonstraci RL v Multipongu."""

    def __init__(self, lr: float = 0.1, gamma: float = 0.9, epsilon: float = 0.1) -> None:
        self.lr = float(lr)
        self.gamma = float(gamma)
        self.epsilon = float(epsilon)
        self.Q: Dict[State, Dict[int, float]] = {}
        self.last_state: State | None = None
        self.last_action: int | None = None

    def get_actions(self) -> List[int]:
        return [0, 1, 2]  # 0: stay, 1: up, 2: down

    def encode_state(self, paddle: "Paddle", ball: "Ball") -> State:
        zone = int((ball.y - paddle.y) // 30)
        direction = 1 if ball.vy > 0 else (-1 if ball.vy < 0 else 0)
        speed = int(abs(ball.vx) // 2)
        return (zone, direction, speed)

    def decide(self, paddle: "Paddle", ball: "Ball", arena: "Arena") -> Action:  # noqa: ARG002
        state = self.encode_state(paddle, ball)
        self._ensure_state(state)

        if random.random() < self.epsilon:
            action = random.choice(self.get_actions())
        else:
            q_state = self.Q[state]
            action = max(q_state, key=q_state.get)

        self.last_state = state
        self.last_action = action
        return self._action_to_flags(action)

    def give_reward(self, paddle: "Paddle", ball: "Ball", reward: float) -> None:
        if self.last_state is None or self.last_action is None:
            return

        next_state = self.encode_state(paddle, ball)
        self._ensure_state(next_state)
        self._ensure_state(self.last_state)

        best_next = max(self.Q[next_state].values()) if self.Q[next_state] else 0.0
        old_value = self.Q[self.last_state][self.last_action]
        updated = old_value + self.lr * (reward + self.gamma * best_next - old_value)
        self.Q[self.last_state][self.last_action] = updated

    def reset_episode(self) -> None:
        """Vymaže paměť posledního stavu/akce (např. při novém utkání)."""
        self.last_state = None
        self.last_action = None

    def _ensure_state(self, state: State) -> None:
        if state not in self.Q:
            self.Q[state] = {a: 0.0 for a in self.get_actions()}

    @staticmethod
    def _action_to_flags(action: int) -> Action:
        return {"up": action == 1, "down": action == 2}

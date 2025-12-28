"""Q-learning AI agent pro MULTIPONG.

Udržuje Q tabulku ve tvaru ``Q[(state)][action]`` a používá epsilon-greedy
politiku pro výběr akce.

Umí také načíst natrénovaný model ze souboru (z notebooku).
"""

from __future__ import annotations

import pickle
import random
from pathlib import Path
from typing import Dict, List, Tuple, TYPE_CHECKING

from .base_ai import Action, BaseAI

if TYPE_CHECKING:  # typové importy pouze pro lint/IDE
    from multipong.engine import Arena, Ball, Paddle

State = Tuple[int, int, int]


class QLearningAI(BaseAI):
    """Jednoduchý Q-learning agent pro demonstraci RL v Multipongu."""

    def __init__(
        self,
        lr: float = 0.1,
        gamma: float = 0.9,
        epsilon: float = 0.1,
        model_path: str | None = None,
    ) -> None:
        self.lr = float(lr)
        self.gamma = float(gamma)
        self.epsilon = float(epsilon)
        self.Q: Dict[State, Dict[int, float]] = {}
        self.last_state: State | None = None
        self.last_action: int | None = None

        # Pokus se načíst model ze souboru
        if model_path:
            self._load_model(model_path)

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

    def _load_model(self, model_path: str) -> None:
        """Načte naučenou Q-tabulku z souboru.

        Args:
            model_path: Cesta k souboru Q-tabule (pickle formát)
        """
        path = Path(model_path)
        if path.exists():
            try:
                with open(path, "rb") as f:
                    self.Q = pickle.load(f)
                # Vypni exploraci pokud máme naučený model
                self.epsilon = 0.0
            except Exception as e:
                print(f"⚠️ Chyba při načítání modelu z {model_path}: {e}")
        else:
            print(f"⚠️ Soubor modelu nenalezen: {model_path}")

    def save_model(self, model_path: str) -> None:
        """Uloží aktuální Q-tabulku do souboru.

        Args:
            model_path: Cesta k souboru (bude vytvořen)
        """
        path = Path(model_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.Q, f)

    def _ensure_state(self, state: State) -> None:
        if state not in self.Q:
            self.Q[state] = {a: 0.0 for a in self.get_actions()}

    @staticmethod
    def _action_to_flags(action: int) -> Action:
        return {"up": action == 1, "down": action == 2}

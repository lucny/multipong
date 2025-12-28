"""Utility funkce pro RL trénink."""

from __future__ import annotations

import numpy as np

from .rl_env import RLPongEnv, State


def encode_state(state: State, env: RLPongEnv, num_bins: int = 10) -> tuple:
    """
    Diskretizuje stav do klíče pro Q-tabuli.

    Args:
        state: Stav z RLPongEnv
        env: Instance prostředí
        num_bins: Počet binů pro diskretizaci

    Returns:
        Tuple (rel_bin, dir_y) jako klíč pro Q-tabulku
    """
    # Relativní pozice míčku vůči pálce
    rel_y = state.ball_y - state.paddle_y
    rel_y_norm = rel_y / env.height if env.height > 0 else 0.5
    rel_bin = int(max(0, min(1.0, rel_y_norm)) * (num_bins - 1))

    # Směr pohybu míčku (vertikální)
    dir_y = 0 if abs(state.ball_vy) < 0.01 else (1 if state.ball_vy > 0 else -1)

    return (rel_bin, dir_y)


def get_q_value(q_table: dict, state_key: tuple, action: int = None) -> float | np.ndarray:
    """
    Bezpečně získá Q-hodnotu ze tabulky.

    Args:
        q_table: Slovník Q-tabulky
        state_key: Klíč stavu
        action: Volitelná akce (pokud None, vrátí celý vektor)

    Returns:
        Q-hodnota pro akci nebo vektor všech Q-hodnot
    """
    if state_key not in q_table:
        q_table[state_key] = np.zeros(3)  # 3 akce: stay, up, down

    if action is not None:
        return q_table[state_key][action]
    return q_table[state_key]


def update_q_value(
    q_table: dict,
    state_key: tuple,
    action: int,
    next_state_key: tuple,
    reward: float,
    alpha: float = 0.1,
    gamma: float = 0.95,
) -> None:
    """
    Aktualizuje Q-hodnotu pomocí Q-learning update.

    Q(s,a) <- Q(s,a) + alpha * (reward + gamma * max(Q(s',a')) - Q(s,a))
    """
    get_q_value(q_table, state_key)  # Inicializuj pokud neexistuje
    get_q_value(q_table, next_state_key)  # Inicializuj pokud neexistuje

    old_value = q_table[state_key][action]
    max_next = np.max(q_table[next_state_key])
    new_value = old_value + alpha * (reward + gamma * max_next - old_value)
    q_table[state_key][action] = new_value

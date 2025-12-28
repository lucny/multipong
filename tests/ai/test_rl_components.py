"""Testy pro RL komponenty (RLPongEnv, utilities, model persistence)."""

import pickle
import tempfile
from pathlib import Path

from multipong.ai import (
    RLPongEnv,
    QLearningAI,
    encode_state,
    get_q_value,
    update_q_value,
)


def test_rl_pong_env_basic() -> None:
    """Test základní funkčnosti RLPongEnv."""
    env = RLPongEnv(width=400, height=300)
    state = env.reset()

    assert state.ball_x == 200.0
    assert state.ball_y == 150.0
    assert state.paddle_y == 120.0  # center - half_height


def test_rl_pong_env_step() -> None:
    """Test kroku v prostředí."""
    env = RLPongEnv()
    state = env.reset()

    next_state, reward, done = env.step(action=0)  # stay

    assert not done
    assert next_state.ball_x != state.ball_x  # míček se pohnul
    assert isinstance(reward, float)


def test_rl_pong_env_paddle_collision() -> None:
    """Test kolize s pálkou."""
    env = RLPongEnv(width=400, height=300, paddle_height=60)
    state = env.reset()

    # Nastav míček těsně před pálkou v správné výšce
    env.ball_x = 15.0
    env.ball_y = env.paddle_y + 30.0  # střed pálky
    env.ball_vx = -2.0

    next_state, reward, done = env.step(action=0)

    assert reward == 1.0  # zásah
    assert not done


def test_rl_pong_env_miss() -> None:
    """Test netrefení."""
    env = RLPongEnv()
    state = env.reset()

    # Nastav míček mimo pálku
    env.ball_x = 15.0
    env.ball_y = 0.0
    env.ball_vx = -2.0
    env.paddle_y = 200.0  # pálka je jinde

    next_state, reward, done = env.step(action=0)

    assert reward == -5.0
    assert done is True


def test_encode_state() -> None:
    """Test diskretizace stavu."""
    env = RLPongEnv()
    state = env.reset()

    encoded = encode_state(state, env, num_bins=10)

    assert isinstance(encoded, tuple)
    assert len(encoded) == 2
    assert 0 <= encoded[0] < 10  # bin
    assert encoded[1] in [-1, 0, 1]  # direction


def test_get_q_value() -> None:
    """Test bezpečného přístupu k Q-hodnotám."""
    Q = {}
    state_key = (5, 1)

    q_vals = get_q_value(Q, state_key)
    assert len(q_vals) == 3
    assert all(v == 0.0 for v in q_vals)


def test_update_q_value() -> None:
    """Test aktualizace Q-hodnoty."""
    Q = {}
    state_key = (5, 1)
    next_state_key = (6, 1)

    update_q_value(Q, state_key, action=1, next_state_key=next_state_key, reward=1.0)

    assert state_key in Q
    assert Q[state_key][1] > 0.0  # q-hodnota by měla stoupnout


def test_qlearning_ai_model_persistence() -> None:
    """Test uložení a načtení modelu."""
    ai = QLearningAI(lr=0.2, epsilon=0.1)

    # Přidej nějaké dummy Q-hodnoty
    ai.Q[(5, 1)] = {0: 0.5, 1: 1.2, 2: 0.3}

    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / "test_model.pkl"

        # Ulož
        ai.save_model(str(model_path))
        assert model_path.exists()

        # Vytvoř nový AI a načti
        ai2 = QLearningAI()
        ai2._load_model(str(model_path))

        assert (5, 1) in ai2.Q
        assert ai2.Q[(5, 1)][1] == 1.2


def test_qlearning_ai_constructor_with_model() -> None:
    """Test konstruktoru s model_path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / "model.pkl"

        # Vytvoř a ulož model
        ai = QLearningAI()
        ai.Q[(3, -1)] = {0: 0.1, 1: 0.2, 2: 0.3}
        ai.save_model(str(model_path))

        # Vytvoř nový AI s model_path v konstruktoru
        ai_loaded = QLearningAI(model_path=str(model_path))

        assert (3, -1) in ai_loaded.Q
        assert ai_loaded.Q[(3, -1)][2] == 0.3
        assert ai_loaded.epsilon == 0.0  # explorace by měla být vypnuta

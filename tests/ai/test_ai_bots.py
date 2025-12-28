"""Testy pro AI hráče v MULTIPONG."""

from multipong.ai import (
    PredictiveAI,
    QLearningAI,
    SimpleAI,
    StaticAI,
    assign_ai_to_slots,
    assign_ai_to_team,
    clear_team_ai,
)
from multipong.engine import Arena, Ball, MultipongEngine, Paddle


def test_simple_ai_moves_towards_ball() -> None:
    ai = SimpleAI(dead_zone=0)
    paddle = Paddle(x=0, y=50, height=100, player_id="A9")
    ball = Ball(x=0, y=10)
    arena = Arena(width=200, height=200)

    action = ai.decide(paddle, ball, arena)

    assert action["up"] is True
    assert action["down"] is False


def test_static_ai_never_moves() -> None:
    ai = StaticAI()
    paddle = Paddle(x=0, y=50, height=100, player_id="A5")
    ball = Ball(x=0, y=10)
    arena = Arena(width=200, height=200)

    action = ai.decide(paddle, ball, arena)

    assert action["up"] is False
    assert action["down"] is False


def test_predictive_ai_anticipates_future_position() -> None:
    ai = PredictiveAI(prediction_steps=60, noise=0)
    paddle = Paddle(x=0, y=380, height=40, player_id="B2")
    ball = Ball(x=0, y=200, vx=5, vy=4, radius=8)
    arena = Arena(width=800, height=800)

    action = ai.decide(paddle, ball, arena)

    assert action["down"] is True
    assert action["up"] is False


def test_qlearning_ai_updates_q_table() -> None:
    ai = QLearningAI(lr=0.5, gamma=0.9, epsilon=0.0)
    paddle = Paddle(x=0, y=60, height=80, player_id="A3")
    ball = Ball(x=0, y=90, vx=4, vy=1)
    arena = Arena(width=300, height=300)

    ai.decide(paddle, ball, arena)
    ai.give_reward(paddle, ball, reward=2.0)

    state = ai.encode_state(paddle, ball)

    assert state in ai.Q
    assert ai.last_action == 0
    assert ai.Q[state][ai.last_action] > 0


def test_assign_ai_to_team() -> None:
    engine = MultipongEngine()
    team = engine.team_left

    assign_ai_to_team(team, level=1)

    for paddle in team.paddles:
        assert paddle.ai is not None
        assert isinstance(paddle.ai, SimpleAI)


def test_assign_ai_to_specific_slots() -> None:
    engine = MultipongEngine(num_players_per_team=4)
    team = engine.team_right

    assign_ai_to_slots(team, slot_indices=[0, 2], level=2)

    assert isinstance(team.paddles[0].ai, PredictiveAI)
    assert team.paddles[1].ai is None
    assert isinstance(team.paddles[2].ai, PredictiveAI)
    if len(team.paddles) > 3:
        assert team.paddles[3].ai is None


def test_clear_team_ai() -> None:
    engine = MultipongEngine()
    team = engine.team_left

    assign_ai_to_team(team, level=1)
    assert all(p.ai is not None for p in team.paddles)

    clear_team_ai(team)
    assert all(p.ai is None for p in team.paddles)


def test_engine_uses_ai_when_assigned() -> None:
    engine = MultipongEngine()
    paddle = engine.paddles["A1"]
    paddle.ai = SimpleAI(dead_zone=0)

    engine.ball.vx = 0
    engine.ball.vy = 0
    engine.ball.y = max(5, paddle.y - 30)

    previous_y = paddle.y
    engine.update({})

    assert paddle.y < previous_y, "AI by měla pálku posunout nahoru směrem k míčku"


def test_paddle_snapshot_includes_ai_class_name() -> None:
    paddle = Paddle(x=100, y=200, player_id="B3")
    paddle.ai = PredictiveAI()

    snapshot = paddle.to_dict()

    assert snapshot["ai_class_name"] == "PredictiveAI"

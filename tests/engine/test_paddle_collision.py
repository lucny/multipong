"""Testy kolize míčku s pálkami."""
from multipong.engine.game_engine import MultipongEngine


def test_ball_collides_left_paddle_changes_direction():
    engine = MultipongEngine()
    engine.start()
    left = engine.paddles["A1"]
    # Nastav míček těsně vpravo od pálky a nech ho letět doleva
    engine.ball.x = left.x + left.width + engine.ball.radius + 1
    engine.ball.y = left.y + left.height / 2
    engine.ball.vx = -5
    prev_vx = engine.ball.vx
    engine.update({})  # žádné vstupy
    assert engine.ball.vx > 0, "Míček by měl po kolizi letět doprava (invertovaný vx)."
    assert engine.ball.vx != prev_vx


def test_ball_collides_right_paddle_changes_direction():
    engine = MultipongEngine()
    engine.start()
    right = engine.paddles["B1"]
    # Nastav míček těsně vlevo od pálky a nech ho letět doprava
    engine.ball.x = right.x - engine.ball.radius - 1
    engine.ball.y = right.y + right.height / 2
    engine.ball.vx = 5
    prev_vx = engine.ball.vx
    engine.update({})
    assert engine.ball.vx < 0, "Míček by měl po kolizi letět doleva (invertovaný vx)."
    assert engine.ball.vx != prev_vx

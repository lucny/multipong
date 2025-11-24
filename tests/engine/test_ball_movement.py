"""Testy pohybu a odrazu míčku Ball."""
from multipong.engine.ball import Ball
from multipong import settings


def test_ball_moves_basic():
    b = Ball(settings.WINDOW_WIDTH / 2, settings.WINDOW_HEIGHT / 2, vx=3.0, vy=4.0)
    x0, y0 = b.x, b.y
    b.update()
    assert b.x == x0 + 3.0
    assert b.y == y0 + 4.0


def test_ball_bounce_bottom():
    b = Ball(settings.WINDOW_WIDTH / 2, settings.WINDOW_HEIGHT - 20, vx=0, vy=15.0, radius=10)
    b.update()  # Posune se dolů a měl by se odrazit
    assert b.vy < 0, "Vy by se měl invertovat (odraz od spodní hrany)."
    assert b.y == settings.WINDOW_HEIGHT - b.radius, "Míček má být naklapnut na dolní hranici."


def test_ball_bounce_top():
    b = Ball(settings.WINDOW_WIDTH / 2, 15, vx=0, vy=-20.0, radius=10)
    b.update()  # Posune se nahoru a měl by se odrazit
    assert b.vy > 0, "Vy by se měl invertovat (odraz od horní hrany)."
    assert b.y == b.radius, "Míček má být naklapnut na horní hranici."


def test_ball_reset_center():
    b = Ball(100, 100, vx=2, vy=2)
    b.reset()
    assert b.x == settings.WINDOW_WIDTH / 2
    assert b.y == settings.WINDOW_HEIGHT / 2

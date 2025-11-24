"""
Testy pro Ball třídu
"""

import pytest
from multipong.engine.ball import Ball


def test_ball_creation():
    """Test vytvoření míčku."""
    ball = Ball(x=100, y=100, vx=5, vy=3)
    assert ball.x == 100
    assert ball.y == 100
    assert ball.vx == 5
    assert ball.vy == 3
    assert ball.radius == 10.0  # Default hodnota


def test_ball_to_dict():
    """Test serializace míčku do slovníku."""
    ball = Ball(x=50, y=75, vx=3, vy=-2, radius=8)
    ball_dict = ball.to_dict()
    
    assert ball_dict["x"] == 50
    assert ball_dict["y"] == 75
    assert ball_dict["vx"] == 3
    assert ball_dict["vy"] == -2
    assert ball_dict["radius"] == 8


def test_ball_update_placeholder():
    """Test že update metoda existuje (implementace později)."""
    ball = Ball(x=0, y=0, vx=10, vy=5)
    # Zatím jen kontrola, že metoda nehodí chybu
    ball.update()
    # TODO: Až bude implementováno, otestovat skutečný pohyb


def test_ball_reset():
    """Reset vrací míček do středu dle settings (signature bez parametrů)."""
    ball = Ball(x=100, y=100)
    ball.reset()
    # Kontrolu konkrétní hodnoty řeší samostatný test v test_ball_movement.py (reset_center)
    assert isinstance(ball.x, float)
    assert isinstance(ball.y, float)


def test_ball_reverse_methods():
    """reverse_x / reverse_y invertují příslušné rychlosti."""
    ball = Ball(x=50, y=50, vx=5, vy=-7)
    ball.reverse_x()
    assert ball.vx == -5
    ball.reverse_y()
    assert ball.vy == 7

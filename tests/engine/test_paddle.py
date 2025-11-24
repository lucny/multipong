"""
Testy pro Paddle třídu
"""

import pytest
from multipong.engine.paddle import Paddle


def test_paddle_creation():
    """Test vytvoření pálky."""
    paddle = Paddle(x=50, y=100, width=20, height=100, speed=5)
    assert paddle.x == 50
    assert paddle.y == 100
    assert paddle.width == 20
    assert paddle.height == 100
    assert paddle.speed == 5


def test_paddle_with_player_id():
    """Test vytvoření pálky s player ID."""
    paddle = Paddle(x=100, y=200, player_id="A1")
    assert paddle.player_id == "A1"


def test_paddle_to_dict():
    """Test serializace pálky do slovníku."""
    paddle = Paddle(x=50, y=100, width=15, height=80, player_id="B2")
    paddle_dict = paddle.to_dict()
    
    assert paddle_dict["x"] == 50
    assert paddle_dict["y"] == 100
    assert paddle_dict["width"] == 15
    assert paddle_dict["height"] == 80
    assert paddle_dict["player_id"] == "B2"


def test_paddle_move_methods_exist():
    """Test že metody pro pohyb existují."""
    paddle = Paddle(x=50, y=100)
    # Zatím jen kontrola, že metody nehodí chybu
    paddle.move_up()
    paddle.move_down()
    # TODO: Až bude implementováno, otestovat skutečný pohyb


def test_paddle_update_placeholder():
    """Test že update metoda existuje."""
    paddle = Paddle(x=50, y=100)
    paddle.update(arena_height=600)
    # TODO: Až bude implementováno, otestovat omezení pohybu

"""
Testy pro MultipongEngine
"""

import pytest
from multipong.engine.game_engine import MultipongEngine


def test_engine_creation():
    """Test vytvoření enginu."""
    engine = MultipongEngine()
    assert engine is not None
    assert engine.arena is not None
    assert engine.ball is not None


def test_engine_with_custom_arena_size():
    """Test vytvoření enginu s vlastními rozměry."""
    engine = MultipongEngine(arena_width=1000, arena_height=600)
    assert engine.arena.width == 1000
    assert engine.arena.height == 600


def test_engine_initial_paddles():
    """Test že engine vytvoří výchozí pálky."""
    engine = MultipongEngine()
    assert "A1" in engine.paddles
    assert "B1" in engine.paddles
    assert len(engine.paddles) == 2


def test_engine_initial_score():
    """Test výchozího skóre."""
    engine = MultipongEngine()
    assert engine.score["A"] == 0
    assert engine.score["B"] == 0


def test_engine_initial_state():
    """Test výchozího stavu hry."""
    engine = MultipongEngine()
    assert engine.is_running is False
    assert engine.time_left == 120.0


def test_engine_get_state():
    """Test získání stavu hry jako slovníku."""
    engine = MultipongEngine()
    state = engine.get_state()
    
    assert "ball" in state
    assert "paddles" in state
    assert "score" in state
    assert "time_left" in state
    assert "is_running" in state
    assert "arena" in state
    
    # Kontrola struktury
    assert "A1" in state["paddles"]
    assert "B1" in state["paddles"]
    assert state["score"]["A"] == 0
    assert state["score"]["B"] == 0


def test_engine_start_stop():
    """Test spuštění a zastavení hry."""
    engine = MultipongEngine()
    
    # Výchozí stav
    assert engine.is_running is False
    
    # Start
    engine.start()
    assert engine.is_running is True
    
    # Stop
    engine.stop()
    assert engine.is_running is False


def test_engine_update_method_exists():
    """Test že update metoda existuje."""
    engine = MultipongEngine()
    inputs = {"A1": {"up": False, "down": False}}
    
    # Zatím jen kontrola, že metoda nehodí chybu
    engine.update(inputs)
    # TODO: Až bude implementováno, otestovat skutečnou aktualizaci

"""
Testy pro Arena třídu
"""

import pytest
from multipong.engine.arena import Arena


def test_arena_creation():
    """Test vytvoření arény."""
    arena = Arena(width=1200, height=800)
    assert arena.width == 1200
    assert arena.height == 800


def test_arena_default_size():
    """Test výchozích rozměrů arény."""
    arena = Arena()
    assert arena.width == 1200
    assert arena.height == 800


def test_arena_get_center():
    """Test získání středu arény."""
    arena = Arena(width=1200, height=800)
    center = arena.get_center()
    assert center == (600, 400)


def test_arena_get_dimensions():
    """Test získání rozměrů arény."""
    arena = Arena(width=1000, height=600)
    dims = arena.get_dimensions()
    assert dims == (1000, 600)


def test_arena_is_out_of_bounds():
    """Test detekce pozice mimo arenu."""
    arena = Arena(width=1200, height=800)
    
    # Pozice uvnitř
    assert arena.is_out_of_bounds(100, 100) is False
    assert arena.is_out_of_bounds(600, 400) is False
    
    # Pozice mimo
    assert arena.is_out_of_bounds(-10, 100) is True
    assert arena.is_out_of_bounds(100, -10) is True
    assert arena.is_out_of_bounds(1300, 100) is True
    assert arena.is_out_of_bounds(100, 900) is True


def test_arena_to_dict():
    """Test serializace arény do slovníku."""
    arena = Arena(width=800, height=600)
    arena_dict = arena.to_dict()
    
    assert arena_dict["width"] == 800
    assert arena_dict["height"] == 600

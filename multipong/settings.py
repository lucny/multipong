"""Globální nastavení projektu MULTIPONG.

Konfigurace je nyní načítána z multipong/config/config.json pomocí config_loader.
Všechny parametry jsou pro pohodlí zde znovu vystaveny.
"""

from __future__ import annotations

from typing import Dict

# Načteme konfiguraci ze config_loader
from multipong.config.config_loader import load_config, get as config_get

# Inicializujeme konfiguraci
_config = load_config()


# Rozměry okna / arény
WINDOW_WIDTH: int = int(config_get("game.arena_width", 1200))
WINDOW_HEIGHT: int = int(config_get("game.arena_height", 800))

# Výchozí parametry míčku
BALL_RADIUS: int = int(config_get("ball.radius", 10))
BALL_SPEED_X: float = float(config_get("ball.speed_x", 6.0))
BALL_SPEED_Y: float = float(config_get("ball.speed_y", 4.0))
BALL_SPEED_INCREMENT: float = float(config_get("ball.speed_increment_on_hit", 0.2))

# Velikost branky
GOAL_SIZE: int = int(config_get("goals.size", 200))

# Délka pauzy po gólu (sekundy)
GOAL_PAUSE_SECONDS: float = 1.0

# Výška pálky
PADDLE_HEIGHT: int = int(config_get("paddles.height", 100))

# Šířka pálky
PADDLE_WIDTH: int = int(config_get("paddles.width", 20))

# Počet pálek na tým
PADDLES_COUNT_PER_TEAM: int = int(config_get("paddles.count_per_team", 4))

# Rychlost pálek
PADDLE_SPEED: int = int(config_get("paddles.speed", 6))

# Per-slot výšky pálek (pokud definováno)
PADDLE_HEIGHTS: Dict[str, int] = {}
paddle_heights_config = config_get("paddles.heights", {})
if isinstance(paddle_heights_config, dict):
    PADDLE_HEIGHTS = {k: int(v) for k, v in paddle_heights_config.items() if isinstance(v, (int, float))}

# Režim neomezeného pohybu pálek v ose Y
PADDLES_UNRESTRICTED_Y: bool = False

# Parametr pro postupné snižování rychlosti míčku
BALL_SPEED_DECAY: float = 1.0
BALL_SPEED_DECAY_X: float = 1.0
BALL_SPEED_DECAY_Y: float = 1.0
BALL_SPEED_MAX: float = 12.0

# Stretch efekt konfigurace
PADDLE_HIT_STRETCH: float = 1.3
PADDLE_STRETCH_DECAY: float = 0.92

# Rally adapt faktor
RALLY_ADAPT_FACTOR: float = 0.05

# FPS pro klienta
DEFAULT_FPS: int = int(config_get("client.fps", 60))

# Server tick rate (Hz) - frekvence game loop aktualizací
SERVER_TICK_RATE: int = int(config_get("server.tick_rate", 60))

__all__ = [
	"WINDOW_WIDTH",
	"WINDOW_HEIGHT",
	"BALL_RADIUS",
	"BALL_SPEED_X",
	"BALL_SPEED_Y",
	"BALL_SPEED_INCREMENT",
	"GOAL_SIZE",
	"GOAL_PAUSE_SECONDS",
	"PADDLE_HEIGHT",
	"PADDLE_WIDTH",
	"PADDLES_COUNT_PER_TEAM",
	"PADDLE_SPEED",
	"PADDLE_HEIGHTS",
	"PADDLES_UNRESTRICTED_Y",
	"BALL_SPEED_DECAY",
	"BALL_SPEED_DECAY_X",
	"BALL_SPEED_DECAY_Y",
	"BALL_SPEED_MAX",
	"PADDLE_HIT_STRETCH",
	"PADDLE_STRETCH_DECAY",
	"RALLY_ADAPT_FACTOR",
	"DEFAULT_FPS",
	"SERVER_TICK_RATE",
]

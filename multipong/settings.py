"""Globální nastavení projektu MULTIPONG.

Postupně přecházíme z pevných konstant na konfiguraci načítanou ze souboru
`config.json` v kořenovém adresáři projektu.
Pokud soubor neexistuje nebo klíč chybí, použijí se bezpečné defaulty.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Načtení config.json (volitelné)
# ---------------------------------------------------------------------------
_CONFIG_PATH = pathlib.Path(__file__).resolve().parents[1] / "config.json"
_raw_config: Dict[str, Any] = {}
if _CONFIG_PATH.exists():  # pragma: no cover - jednoduché IO
	try:
		_raw_config = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
	except Exception:  # pragma: no cover - při chybě ignorujeme
		_raw_config = {}


# Helper pro čtení hodnot s fallbackem
def _cfg(key: str, default: Any) -> Any:
	return _raw_config.get(key, default)


# Rozměry okna / arény (musí ladit s inicializací MultipongEngine v klientovi)
WINDOW_WIDTH: int = int(_cfg("window_width", 1200))
WINDOW_HEIGHT: int = int(_cfg("window_height", 800))

# Výchozí parametry míčku
BALL_RADIUS: int = 10
BALL_SPEED_X: float = 5.0
BALL_SPEED_Y: float = 5.0
BALL_SPEED_INCREMENT: float = float(_cfg("ball_speed_increment", 0.2))  # Zvýšení rychlosti po každém odrazu od pálky

# Velikost branky (výška vertikálního pásma) – konfigurovatelné
GOAL_SIZE: int = int(_cfg("goal_size", 200))

# Délka pauzy po gólu (sekundy)
GOAL_PAUSE_SECONDS: float = float(_cfg("goal_pause_seconds", 1.0))

# FPS pro klienta (zatím informativní)
DEFAULT_FPS: int = int(_cfg("default_fps", 60))

__all__ = [
	"WINDOW_WIDTH",
	"WINDOW_HEIGHT",
	"BALL_RADIUS",
	"BALL_SPEED_X",
	"BALL_SPEED_Y",
	"BALL_SPEED_INCREMENT",
	"GOAL_SIZE",
	"GOAL_PAUSE_SECONDS",
	"DEFAULT_FPS",
]

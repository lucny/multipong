"""Globální nastavení projektu MULTIPONG.

Později bude nahrazeno načítáním z konfiguračního souboru / databáze.
Phase 1-2: Konstanty přímo v modulu.
"""

# Rozměry okna / arény (musí ladit s inicializací MultipongEngine v klientovi)
WINDOW_WIDTH: int = 1200
WINDOW_HEIGHT: int = 800

# Výchozí parametry míčku
BALL_RADIUS: int = 10
BALL_SPEED_X: float = 5.0
BALL_SPEED_Y: float = 5.0

# FPS pro klienta (zatím informativní)
DEFAULT_FPS: int = 60

"""Ball class - logická reprezentace míčku pro MULTIPONG.

Aktuální verze (Phase 1-2) obsahuje:
- základní pohyb (x += vx, y += vy)
- odraz od horní / dolní stěny dle konstant v settings.py
- jednoduché resetování do středu

Pozdější fáze: jemnější fyzika, spin, náhodná inicializace směru, separace vykreslování.
"""

from __future__ import annotations

from typing import Dict

from multipong import settings


class Ball:
    """Logická entita míčku.

    Attributes:
        x: X souřadnice
        y: Y souřadnice
        vx: Rychlost ve směru X (px/frame)
        vy: Rychlost ve směru Y (px/frame)
        radius: Poloměr míčku
    """

    def __init__(
        self,
        x: float,
        y: float,
        vx: float = settings.BALL_SPEED_X,
        vy: float = settings.BALL_SPEED_Y,
        radius: float = settings.BALL_RADIUS,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius

    def update(self) -> None:
        """Aktualizace pozice + odraz od horní/dolní stěny.

        Odraz:
            - Pokud y - radius <= 0: invert vy, y nastav na radius
            - Pokud y + radius >= WINDOW_HEIGHT: invert vy, y nastav na WINDOW_HEIGHT - radius
        """
        # Pohyb
        self.x += self.vx
        self.y += self.vy

        # Odraz od horní stěny
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.reverse_y()

        # Odraz od dolní stěny
        elif self.y + self.radius >= settings.WINDOW_HEIGHT:
            self.y = settings.WINDOW_HEIGHT - self.radius
            self.reverse_y()

    def reset(self) -> None:
        """Resetuje míček do středu okna (bez změny rychlosti)."""
        self.x = settings.WINDOW_WIDTH / 2
        self.y = settings.WINDOW_HEIGHT / 2

    def reverse_x(self) -> None:
        """Invertuje směr X."""
        self.vx = -self.vx

    def reverse_y(self) -> None:
        """Invertuje směr Y."""
        self.vy = -self.vy

    def to_dict(self) -> Dict[str, float]:
        """Serializace stavu pro síť / debug."""
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "vx": self.vx,
            "vy": self.vy,
        }

    def draw(self, surface) -> None:  # pragma: no cover - vykreslování mimo test scope
        """Placeholder vykreslení (v budoucnu přesun do rendereru)."""
        import pygame

        pygame.draw.circle(
            surface,
            (230, 230, 230),
            (int(self.x), int(self.y)),
            int(self.radius),
        )

"""Základní rozhraní pro AI hráče v MULTIPONG.

AI instance implementují metodu ``decide`` a vrací slovník příznaků pohybu
ve tvaru ``{"up": bool, "down": bool}``.
"""

from __future__ import annotations

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:  # typové importy pouze pro lint/IDE
    from multipong.engine import Arena, Ball, Paddle


Action = Dict[str, bool]


class BaseAI:
    """Abstraktní základ pro všechny AI pálky."""

    def decide(self, paddle: "Paddle", ball: "Ball", arena: "Arena") -> Action:
        """Vrátí rozhodnutí AI pro aktuální stav.

        Args:
            paddle: Pálka, kterou AI ovládá
            ball: Aktuální míček
            arena: Herní aréna

        Returns:
            Slovník příznaků pohybu {"up": bool, "down": bool}
        """

        raise NotImplementedError("AI musí implementovat metodu decide().")

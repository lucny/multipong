"""GoalZone - branka v MULTIPONG.

Definuje oblast, přes kterou když míček proletí, je to gól.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ball import Ball


class GoalZone:
    """Branka na jedné straně hřiště.
    
    Attributes:
        x: X-souřadnice branky (0 pro levou, WINDOW_WIDTH pro pravou)
        top: Horní hranice branky (Y)
        bottom: Dolní hranice branky (Y)
    """

    def __init__(self, x: float, top: float, bottom: float) -> None:
        """Inicializace branky.
        
        Args:
            x: X-pozice branky
            top: Horní hranice (Y)
            bottom: Dolní hranice (Y)
        """
        self.x = x
        self.top = top
        self.bottom = bottom

    def check_goal(self, ball: "Ball") -> bool:
        """Kontrola, zda míček proletěl branou.
        
        Args:
            ball: Instance míčku
            
        Returns:
            True pokud míček proletěl branou, jinak False
        """
        # Míček překročil x-souřadnici branky a je ve vertikálním rozsahu
        if self.x == 0:  # Levá branka
            if ball.x - ball.radius <= self.x:
                return self.top <= ball.y <= self.bottom
        else:  # Pravá branka
            if ball.x + ball.radius >= self.x:
                return self.top <= ball.y <= self.bottom
        return False

    def to_dict(self) -> dict:
        """Serializace branky do slovníku."""
        return {
            "x": self.x,
            "top": self.top,
            "bottom": self.bottom,
        }

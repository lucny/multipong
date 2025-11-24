"""Team - tým v MULTIPONG.

Sdružuje hráče (pálky) jednoho týmu a spravuje jejich celkové skóre.
"""

from typing import Dict, List
from .paddle import Paddle


class Team:
    """Reprezentace týmu v hře.
    
    Attributes:
        name: Název týmu (např. "A" nebo "B")
        paddles: Seznam pálek (hráčů) v týmu
        score: Celkové skóre týmu
    """

    def __init__(self, name: str, paddles: List[Paddle]) -> None:
        """Inicializace týmu.
        
        Args:
            name: Název týmu
            paddles: Seznam pálek týmu
        """
        self.name = name
        self.paddles = paddles
        self.score = 0

    def add_score(self) -> None:
        """Přičte gól ke skóre týmu."""
        self.score += 1
        # Zaznamenej gól všem hráčům týmu
        for paddle in self.paddles:
            if hasattr(paddle, 'stats'):
                paddle.stats.record_goal_scored()

    def to_dict(self) -> Dict[str, any]:
        """Serializace týmu do slovníku.
        
        Returns:
            Slovník se stavem týmu
        """
        return {
            "name": self.name,
            "score": self.score,
            "paddles": [
                {
                    "x": p.x,
                    "y": p.y,
                    "width": p.width,
                    "height": p.height,
                    "stats": p.stats.to_dict() if hasattr(p, 'stats') else None,
                }
                for p in self.paddles
            ],
        }

    def reset_score(self) -> None:
        """Reset skóre týmu na 0."""
        self.score = 0

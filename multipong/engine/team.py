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
                    # Pozice a rozměry pro renderer/klienta
                    "x": p.x,
                    "y": p.y,
                    "width": p.width,
                    "height": p.height,
                    # Identifikátor hráče na top-level pro snadnější práci na klientu
                    "player_id": getattr(p, "player_id", getattr(p.stats, "player_id", "")),
                    # Plochá statistická pole (zachována i v nested "stats" pro kompatibilitu testů)
                    "hits": getattr(p.stats, "hits", 0) if hasattr(p, "stats") else 0,
                    "goals_scored": getattr(p.stats, "goals_scored", 0) if hasattr(p, "stats") else 0,
                    "goals_received": getattr(p.stats, "goals_received", 0) if hasattr(p, "stats") else 0,
                    # Původní vnořená struktura statistik kvůli existujícím testům a kompatibilitě
                    "stats": p.stats.to_dict() if hasattr(p, 'stats') else None,
                }
                for p in self.paddles
            ],
        }

    def reset_score(self) -> None:
        """Reset skóre týmu na 0."""
        self.score = 0

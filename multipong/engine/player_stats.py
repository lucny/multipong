"""PlayerStats - statistiky jednotlivého hráče v MULTIPONG.

Sleduje:
- počet zásahů míčku (hits)
- góly vstřelené týmem během jeho účasti (goals_scored)
- góly obdržené v jeho zóně (goals_received)
"""

from typing import Dict


class PlayerStats:
    """Statistiky jednoho hráče (pálky)."""

    def __init__(self, player_id: str) -> None:
        """Inicializace statistik.
        
        Args:
            player_id: Jedinečný identifikátor hráče (např. "A1", "B3")
        """
        self.player_id = player_id
        self.hits = 0  # Počet zásahů míčku pálkou
        self.goals_scored = 0  # Góly vstřelené týmem
        self.goals_received = 0  # Góly obdržené (v zóně hráče)

    def record_hit(self) -> None:
        """Zaznamenání zásahu míčku."""
        self.hits += 1

    def record_goal_scored(self) -> None:
        """Zaznamenání gólu vstřeleného týmem."""
        self.goals_scored += 1

    def record_goal_received(self) -> None:
        """Zaznamenání obdrženého gólu."""
        self.goals_received += 1

    def to_dict(self) -> Dict[str, any]:
        """Serializace statistik do slovníku.
        
        Returns:
            Slovník se statistikami hráče
        """
        return {
            "player_id": self.player_id,
            "hits": self.hits,
            "goals_scored": self.goals_scored,
            "goals_received": self.goals_received,
        }

    def reset(self) -> None:
        """Reset všech statistik na 0."""
        self.hits = 0
        self.goals_scored = 0
        self.goals_received = 0

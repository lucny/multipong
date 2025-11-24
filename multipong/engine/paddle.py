"""
Paddle class - Pálka pro MULTIPONG engine
Logická reprezentace pálky - nezávislá na Pygame.
"""

from typing import Dict, Optional
from .player_stats import PlayerStats


class Paddle:
    """
    Logická reprezentace jedné pálky - bez grafiky.
    
    Attributes:
        x: X souřadnice pozice
        y: Y souřadnice pozice
        width: Šířka pálky
        height: Výška pálky
        speed: Rychlost pohybu pálky
        player_id: ID hráče/slotu (např. "A1", "B2")
        zone_top: Horní hranice povolené zóny pohybu (None = bez omezení)
        zone_bottom: Dolní hranice povolené zóny pohybu (None = bez omezení)
        stats: Statistiky hráče (PlayerStats instance)
    """
    
    def __init__(
        self, 
        x: float, 
        y: float, 
        width: float = 20.0, 
        height: float = 100.0, 
        speed: float = 5.0,
        player_id: str = "P1",
        zone_top: Optional[float] = None,
        zone_bottom: Optional[float] = None,
        stats: Optional[PlayerStats] = None,
    ):
        """
        Inicializace pálky.
        
        Args:
            x: Počáteční X pozice
            y: Počáteční Y pozice
            width: Šířka pálky
            height: Výška pálky
            speed: Rychlost pohybu
            player_id: ID hráče
            zone_top: Horní hranice zóny (None = bez omezení)
            zone_bottom: Dolní hranice zóny (None = bez omezení)
            stats: Instance PlayerStats (vytvoří se automaticky pokud není zadána)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.player_id = player_id
        self.zone_top = zone_top
        self.zone_bottom = zone_bottom
        self.stats = stats if stats is not None else PlayerStats(player_id)
    
    def move_up(self) -> None:
        """Posune pálku nahoru o konstantní rychlost."""
        self.y -= self.speed

    def move_down(self) -> None:
        """Posune pálku dolů o konstantní rychlost."""
        self.y += self.speed

    def update(self, arena_height: int = 600) -> None:
        """
        Aktualizace pálky – omezí ji na prostor arény nebo zóny.
        
        Args:
            arena_height: Výška arény (použije se pokud nejsou definovány zóny)
        """
        # Použij zóny pokud jsou definovány, jinak celou arénu
        top_limit = self.zone_top if self.zone_top is not None else 0
        bottom_limit = self.zone_bottom if self.zone_bottom is not None else arena_height
        
        self.clamp_to_arena(bottom_limit, top_limit)

    def clamp_to_arena(self, arena_height: int, arena_top: int = 0) -> None:
        """Zabrání pálce opustit arénu nebo zónu.
        
        Args:
            arena_height: Spodní hranice
            arena_top: Horní hranice
        """
        if self.y < arena_top:
            self.y = arena_top
        if self.y + self.height > arena_height:
            self.y = arena_height - self.height
    
    def to_dict(self) -> Dict[str, any]:
        """
        Vrátí stav pálky jako slovník (pro síťovou synchronizaci).
        
        Returns:
            Slovník s pozicí a rozměry pálky
        """
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "player_id": self.player_id,
            "zone_top": self.zone_top,
            "zone_bottom": self.zone_bottom,
            "stats": self.stats.to_dict() if self.stats else None,
        }
    
    def draw(self, surface) -> None:
        """
        Placeholder pro vykreslení pálky.
        V Phase 1–2 lze kreslit přímo zde.
        """
        import pygame
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            pygame.Rect(self.x, self.y, self.width, self.height)
        )

"""
Paddle class - Pálka pro MULTIPONG engine
Logická reprezentace pálky - nezávislá na Pygame.
"""

from typing import Dict


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
    """
    
    def __init__(
        self, 
        x: float, 
        y: float, 
        width: float = 20.0, 
        height: float = 100.0, 
        speed: float = 5.0,
        player_id: str = "P1"
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
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.player_id = player_id
    
    def move_up(self) -> None:
        """Posune pálku nahoru."""
        # TODO: Implementovat pohyb nahoru
        pass
    
    def move_down(self) -> None:
        """Posune pálku dolů."""
        # TODO: Implementovat pohyb dolů
        pass
    
    def update(self, arena_height: int = 600) -> None:
        """
        Aktualizuje pálku a omezí pohyb v rámci arény.
        
        Args:
            arena_height: Výška arény pro omezení pohybu
        """
        # TODO: Implementovat omezení pohybu
        pass
    
    def clamp_to_arena(self, arena_height: int) -> None:
        """
        Omezí pohyb pálky v rámci arény.
        
        Args:
            arena_height: Výška arény
        """
        # TODO: Implementovat clamping
        pass
    
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
            "player_id": self.player_id
        }
    
    def draw(self, surface) -> None:
        """
        Vykreslí pálku na surface (Pygame).
        POZNÁMKA: Podle architektury by draw() mělo být v UI vrstvě,
        ale pro jednoduchost Phase 1-2 zde jako placeholder.
        
        Args:
            surface: Pygame surface pro vykreslení
        """
        # TODO: Implementovat vykreslení (nebo přesunout do UI vrstvy)
        pass

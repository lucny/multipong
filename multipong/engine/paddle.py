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
        """Posune pálku nahoru o konstantní rychlost."""
        self.y -= self.speed

    def move_down(self) -> None:
        """Posune pálku dolů o konstantní rychlost."""
        self.y += self.speed

    def update(self, arena_height: int = 600) -> None:
        """
        Aktualizace pálky – omezí ji na prostor arény.
        """
        self.clamp_to_arena(arena_height)

    def clamp_to_arena(self, arena_height: int) -> None:
        """Zabrání pálce opustit arénu."""
        if self.y < 0:
            self.y = 0
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
            "player_id": self.player_id
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

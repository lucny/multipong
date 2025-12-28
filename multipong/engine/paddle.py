"""
Paddle class - Pálka pro MULTIPONG engine
Logická reprezentace pálky - nezávislá na Pygame.
"""

from typing import Dict, Optional, TYPE_CHECKING
from .player_stats import PlayerStats

if TYPE_CHECKING:  # typové importy pouze pro lint/IDE
    from multipong.ai import BaseAI


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
        ai: Optional["BaseAI"] = None,
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
        self.ai = ai
        # Animace po zásahu (stretch efekt) – parametry z konfigurace
        from multipong import settings  # lokální import kvůli izolaci
        self.stretch_scale: float = 1.0
        self._stretch_decay: float = settings.PADDLE_STRETCH_DECAY  # faktor poklesu za frame
        self._stretch_target: float = 1.0
        self._stretch_hit_factor: float = settings.PADDLE_HIT_STRETCH
    
    def move_up(self) -> None:
        """Posune pálku nahoru o konstantní rychlost."""
        self.y -= self.speed

    def move_down(self) -> None:
        """Posune pálku dolů o konstantní rychlost."""
        self.y += self.speed

    def update(self, arena_height: int = 600, unrestricted: bool = True) -> None:
        """
        Aktualizace pálky – nyní vždy umožňuje pohyb v celé výšce arény
        (požadavek: neomezený pohyb v ose Y), přesto zachovává původní
        hodnoty zone_top/zone_bottom pro kompatibilitu testů.

        Args:
            arena_height: Výška arény
        """
        if unrestricted:
            # Ignoruj zóny – plný rozsah 0 .. arena_height
            self.clamp_to_arena(arena_height, 0)
        else:
            # Respektuj zónu pokud definována
            top_limit = self.zone_top if self.zone_top is not None else 0
            bottom_limit = self.zone_bottom if self.zone_bottom is not None else arena_height
            self.clamp_to_arena(bottom_limit, top_limit)

        # Decay stretch efektu
        if self.stretch_scale > 1.001:
            self.stretch_scale = (self.stretch_scale - 1.0) * self._stretch_decay + 1.0
        else:
            self.stretch_scale = 1.0

    def apply_hit_effect(self) -> None:
        """Aktivuje krátký stretch efekt při zásahu míčku podle konfigurace."""
        self.stretch_scale = self._stretch_hit_factor
        self._stretch_target = 1.0

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
            "ai_class_name": self.ai.__class__.__name__ if self.ai else None,
        }
    
    def draw(self, surface) -> None:
        """
        Placeholder pro vykreslení pálky.
        V Phase 1–2 lze kreslit přímo zde.
        """
        import pygame
        scaled_height = int(self.height * self.stretch_scale)
        # Udrž střed pálky při stretch – posun Y, aby střed zůstal stabilní
        center_y = self.y + self.height / 2
        draw_y = int(center_y - scaled_height / 2)
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            pygame.Rect(self.x, draw_y, self.width, scaled_height),
            border_radius=3,
        )

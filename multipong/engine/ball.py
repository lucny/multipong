"""
Ball class - Míček pro MULTIPONG engine
Logická reprezentace míčku - nezávislá na Pygame.
"""

from typing import Dict


class Ball:
    """
    Logická reprezentace míčku - bez grafiky.
    
    Attributes:
        x: X souřadnice pozice
        y: Y souřadnice pozice
        vx: Rychlost ve směru X
        vy: Rychlost ve směru Y
        radius: Poloměr míčku
    """
    
    def __init__(self, x: float, y: float, vx: float = 5.0, vy: float = 5.0, radius: float = 10.0):
        """
        Inicializace míčku.
        
        Args:
            x: Počáteční X pozice
            y: Počáteční Y pozice
            vx: Rychlost ve směru X
            vy: Rychlost ve směru Y
            radius: Poloměr míčku
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
    
    def update(self) -> None:
        """
        Aktualizuje pozici míčku na základě rychlosti.
        Zatím bez kolizní detekce - bude doplněno později.
        """
        # TODO: Implementovat pohyb míčku
        pass
    
    def reset(self, x: float, y: float) -> None:
        """
        Resetuje míček na zadanou pozici.
        
        Args:
            x: Nová X pozice
            y: Nová Y pozice
        """
        # TODO: Implementovat reset pozice
        pass
    
    def reverse_x(self) -> None:
        """Obrátí směr X (odraz od pálky)."""
        # TODO: Implementovat odraz X
        pass
    
    def reverse_y(self) -> None:
        """Obrátí směr Y (odraz od stěny)."""
        # TODO: Implementovat odraz Y
        pass
    
    def to_dict(self) -> Dict[str, float]:
        """
        Vrátí stav míčku jako slovník (pro síťovou synchronizaci).
        
        Returns:
            Slovník s pozicí a poloměrem míčku
        """
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "vx": self.vx,
            "vy": self.vy
        }
    
    def draw(self, surface) -> None:
        """
        Vykreslí míček na surface (Pygame).
        POZNÁMKA: Podle architektury by draw() mělo být v UI vrstvě,
        ale pro jednoduchost Phase 1-2 zde jako placeholder.
        
        Args:
            surface: Pygame surface pro vykreslení
        """
        # TODO: Implementovat vykreslení (nebo přesunout do UI vrstvy)
        pass

"""
Arena class - Hrací plocha pro MULTIPONG engine
Reprezentace herního hřiště.
"""

from typing import Tuple, Dict


class Arena:
    """
    Reprezentace hrací arény.
    Zatím jednoduchá - později zde budou branky, zóny, překážky.
    
    Attributes:
        width: Šířka arény
        height: Výška arény
    """
    
    def __init__(self, width: int = 1200, height: int = 800):
        """
        Inicializace arény.
        
        Args:
            width: Šířka arény
            height: Výška arény
        """
        self.width = width
        self.height = height
    
    def get_center(self) -> Tuple[float, float]:
        """
        Vrátí střed arény.
        
        Returns:
            Tuple (x, y) středu arény
        """
        return (self.width / 2, self.height / 2)
    
    def get_dimensions(self) -> Tuple[int, int]:
        """
        Vrátí rozměry arény.
        
        Returns:
            Tuple (width, height)
        """
        return (self.width, self.height)
    
    def is_out_of_bounds(self, x: float, y: float) -> bool:
        """
        Kontroluje, zda je pozice mimo arenu.
        
        Args:
            x: X souřadnice
            y: Y souřadnice
            
        Returns:
            True pokud je pozice mimo arenu
        """
        return x < 0 or x > self.width or y < 0 or y > self.height
    
    def check_goal(self, ball_x: float, ball_radius: float) -> str:
        """
        Kontroluje, zda míček prošel brankou.
        
        Args:
            ball_x: X pozice míčku
            ball_radius: Poloměr míčku
            
        Returns:
            "left" pro gól vlevo, "right" pro gól vpravo, None jinak
        """
        # TODO: Implementovat detekci gólu
        pass
    
    def to_dict(self) -> Dict[str, int]:
        """
        Vrátí stav arény jako slovník.
        
        Returns:
            Slovník s rozměry arény
        """
        return {
            "width": self.width,
            "height": self.height
        }
    
    def draw(self, surface) -> None:
        """
        Vykreslí arenu na surface (Pygame).
        Zatím placeholder - později střední čára, branky atd.
        
        Args:
            surface: Pygame surface pro vykreslení
        """
        # TODO: Implementovat vykreslení (střední čára, branky)
        pass

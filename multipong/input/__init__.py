"""Input handler abstraction pro MULTIPONG.

Umožňuje dependency inversion: engine nevyžaduje přímo pygame,
jen abstraktní rozhraní pro vstup.
"""

from typing import Dict, Protocol


class InputHandler(Protocol):
    """Protokol pro získávání vstupů od hráčů.
    
    Různé implementace (pygame, websocket, AI bot) implementují toto rozhraní.
    """
    
    def get_inputs(self) -> Dict[str, Dict[str, bool]]:
        """Vrátí slovník vstupů pro všechny hráče.
        
        Returns:
            Dict ve formátu {"A1": {"up": bool, "down": bool}, "B1": {...}, ...}
        """
        ...

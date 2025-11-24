"""Pygame implementace InputHandler."""

from typing import Dict


class PygameInputHandler:
    """Čte vstupy z pygame klávesnice pro lokální demo hru.
    
    Mapování:
    - Levá pálka (A1): W/S
    - Pravá pálka (B1): šipky nahoru/dolů
    """
    
    def __init__(self):
        """Inicializace pygame input handleru."""
        # Import pygame až při použití, aby mohl existovat i bez pygame
        import pygame
        self.pygame = pygame
    
    def get_inputs(self) -> Dict[str, Dict[str, bool]]:
        """Čte aktuální stav klávesnice.
        
        Returns:
            Slovník vstupů {"A1": {"up": bool, "down": bool}, ...}
        """
        keys = self.pygame.key.get_pressed()
        return {
            "A1": {
                "up": keys[self.pygame.K_w],
                "down": keys[self.pygame.K_s],
            },
            "B1": {
                "up": keys[self.pygame.K_UP],
                "down": keys[self.pygame.K_DOWN],
            },
        }

"""
SimpleAI - Reaktivní AI pro MULTIPONG
"""

from typing import Tuple


class SimpleAI:
    """
    Jednoduchá reaktivní AI.
    Sleduje pozici míčku a pohybuje pálkou směrem k němu.
    """
    
    def __init__(self, reaction_speed: float = 0.8):
        """
        Args:
            reaction_speed: Rychlost reakce AI (0.0-1.0)
        """
        self.reaction_speed = reaction_speed
    
    def decide_action(
        self, 
        paddle_y: float, 
        ball_y: float, 
        paddle_height: float
    ) -> str:
        """
        Rozhodne o akci na základě pozice míčku.
        
        Args:
            paddle_y: Y pozice pálky
            ball_y: Y pozice míčku
            paddle_height: Výška pálky
        
        Returns:
            "up", "down", nebo "stay"
        """
        paddle_center = paddle_y + paddle_height / 2
        
        if ball_y < paddle_center - 5:
            return "up"
        elif ball_y > paddle_center + 5:
            return "down"
        else:
            return "stay"

"""
StateBuffer - buffer pro ukládání a interpolaci game state snapshotů.
Zajišťuje plynulý rendering i při nižší frekvenci network update.
"""

import time
from typing import Optional, List, Tuple, Dict, Any


class StateBuffer:
    """
    Uchovává několik posledních snapshotů.
    Klient renderuje interpolovaný stav mezi nimi.
    
    Attributes:
        buffer: Seznam (timestamp, state) tuple
        max_size: Maximální počet uchovávaných snapshotů
    """
    
    def __init__(self, max_size: int = 3):
        """
        Inicializace state bufferu.
        
        Args:
            max_size: Maximální počet uchovávaných snapshotů (default 3)
        """
        self.buffer: List[Tuple[float, dict]] = []
        self.max_size = max_size
    
    def add_state(self, state: dict) -> None:
        """
        Přidá nový snapshot do bufferu s aktuálním timestampem.
        
        Args:
            state: Dictionary se stavem hry (snapshot od serveru)
        """
        timestamp = time.time()
        self.buffer.append((timestamp, state))
        
        # Držíme pouze poslední N snapshotů
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)
    
    def get_latest(self) -> Optional[dict]:
        """
        Vrátí nejnovější snapshot bez interpolace.
        
        Returns:
            Poslední state nebo None pokud buffer je prázdný
        """
        if self.buffer:
            return self.buffer[-1][1]
        return None
    
    def get_interpolated(self, render_delay: float = 0.0) -> Optional[dict]:
        """
        Vrátí interpolovaný stav mezi dvěma posledními snapshoty.
        Pokud to nejde, vrací poslední stav.
        
        Args:
            render_delay: Offset pro vyhlazení (v sekundách, default 0)
            
        Returns:
            Interpolovaný state nebo None pokud buffer je prázdný
        """
        if len(self.buffer) < 2:
            return self.get_latest()
        
        (t1, s1), (t2, s2) = self.buffer[-2], self.buffer[-1]
        
        now = time.time() - render_delay
        
        # Vypočítáme interpolační faktor
        # alpha = 0.0 → používáme s1 (starší)
        # alpha = 1.0 → používáme s2 (novější)
        time_diff = t2 - t1
        if time_diff <= 0:
            return s2
        
        alpha = (now - t1) / time_diff
        alpha = min(1.0, max(0.0, alpha))  # Clamp do <0, 1>
        
        # Vytvoříme interpolovaný stav
        interpolated = {}
        
        # Interpolace míčku
        if "ball" in s2:
            interpolated["ball"] = self._interpolate_ball(s1.get("ball"), s2.get("ball"), alpha)
        
        # Interpolace týmů (včetně pálek)
        if "team_left" in s2:
            interpolated["team_left"] = self._interpolate_team(
                s1.get("team_left"), s2.get("team_left"), alpha
            )
        
        if "team_right" in s2:
            interpolated["team_right"] = self._interpolate_team(
                s1.get("team_right"), s2.get("team_right"), alpha
            )
        
        # Goal zóny kopírujeme bez interpolace (nemění se)
        if "goal_left" in s2:
            interpolated["goal_left"] = s2["goal_left"]
        
        if "goal_right" in s2:
            interpolated["goal_right"] = s2["goal_right"]
        
        return interpolated
    
    def _interpolate_ball(self, ball1: Optional[dict], ball2: Optional[dict], alpha: float) -> dict:
        """
        Interpoluje pozici míčku mezi dvěma snapshoty.
        
        Args:
            ball1: Starší stav míčku
            ball2: Novější stav míčku
            alpha: Interpolační faktor (0.0 - 1.0)
            
        Returns:
            Interpolovaný stav míčku
        """
        if not ball1 or not ball2:
            return ball2 or ball1 or {}
        
        return {
            "x": ball1["x"] * (1 - alpha) + ball2["x"] * alpha,
            "y": ball1["y"] * (1 - alpha) + ball2["y"] * alpha,
            "radius": ball2.get("radius", 10),
            "vx": ball2.get("vx", 0),
            "vy": ball2.get("vy", 0)
        }
    
    def _interpolate_team(self, team1: Optional[dict], team2: Optional[dict], alpha: float) -> dict:
        """
        Interpoluje stav týmu (včetně pálek).
        
        Args:
            team1: Starší stav týmu
            team2: Novější stav týmu
            alpha: Interpolační faktor (0.0 - 1.0)
            
        Returns:
            Interpolovaný stav týmu
        """
        if not team1 or not team2:
            return team2 or team1 or {}
        
        result = {
            "name": team2.get("name", ""),
            "score": team2.get("score", 0),
            "paddles": []
        }
        
        # Interpolace pálek
        paddles1 = team1.get("paddles", [])
        paddles2 = team2.get("paddles", [])
        
        # Předpokládáme stejný počet pálek ve stejném pořadí
        for i in range(min(len(paddles1), len(paddles2))):
            p1 = paddles1[i]
            p2 = paddles2[i]
            
            interpolated_paddle = {
                "player_id": p2.get("player_id", ""),
                "x": p1.get("x", 0) * (1 - alpha) + p2.get("x", 0) * alpha,
                "y": p1.get("y", 0) * (1 - alpha) + p2.get("y", 0) * alpha,
                "width": p2.get("width", 10),
                "height": p2.get("height", 50),
                "hits": p2.get("hits", 0),
                "goals_scored": p2.get("goals_scored", 0),
                "goals_received": p2.get("goals_received", 0)
            }
            result["paddles"].append(interpolated_paddle)
        
        # Pokud team2 má více pálek, přidáme je bez interpolace
        for i in range(len(paddles2)):
            if i >= len(paddles1):
                result["paddles"].append(paddles2[i])
        
        return result
    
    def clear(self) -> None:
        """Vyčistí buffer."""
        self.buffer.clear()
    
    def size(self) -> int:
        """
        Vrátí počet snapshotů v bufferu.
        
        Returns:
            Počet uchovávaných snapshotů
        """
        return len(self.buffer)
    
    def __repr__(self) -> str:
        """Textová reprezentace pro debugging."""
        return f"StateBuffer(size={len(self.buffer)}/{self.max_size})"

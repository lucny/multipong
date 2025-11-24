"""
MultipongEngine - Hlavní herní engine pro MULTIPONG
Logické jádro hry - nezávislé na Pygame.
"""

from typing import Dict, Optional
from .ball import Ball
from .paddle import Paddle
from .arena import Arena


class MultipongEngine:
    """
    Hlavní logický modul hry - NEZÁVISLÝ NA PYGAME.
    
    Řídí:
    - Herní objekty (míček, pálky, aréna)
    - Aktualizaci stavu hry
    - Detekci kolizí
    - Skóre
    - Synchronizaci se síťovým serverem
    
    Attributes:
        arena: Instance Arena
        ball: Instance Ball
        paddles: Slovník pálek {player_id: Paddle}
        score: Slovník skóre {"A": int, "B": int}
        is_running: Zda hra běží
    """
    
    def __init__(self, arena_width: int = 1200, arena_height: int = 800):
        """
        Inicializace herního enginu.
        
        Args:
            arena_width: Šířka arény
            arena_height: Výška arény
        """
        # Herní objekty
        self.arena = Arena(arena_width, arena_height)
        center_x, center_y = self.arena.get_center()
        self.ball = Ball(center_x, center_y)
        
        # Pálky - zatím jednoduché 1v1, později rozšířit na 4v4
        self.paddles: Dict[str, Paddle] = {}
        self._initialize_paddles()
        
        # Skóre
        self.score = {"A": 0, "B": 0}
        
        # Stav hry
        self.is_running = False
        self.time_left = 120.0  # sekund
    
    def _initialize_paddles(self) -> None:
        """Inicializuje základní pálky pro 1v1."""
        # Levá pálka (tým A)
        center_y = self.arena.height / 2
        self.paddles["A1"] = Paddle(
            x=50,
            y=center_y - 50,
            player_id="A1"
        )
        
        # Pravá pálka (tým B)
        self.paddles["B1"] = Paddle(
            x=self.arena.width - 70,
            y=center_y - 50,
            player_id="B1"
        )
    
    def update(self, inputs: Dict[str, Dict[str, bool]]) -> None:
        """Hlavní aktualizační smyčka enginu (placeholder logika).

        Args:
            inputs: Slovník vstupů od hráčů
                    Formát: {"A1": {"up": bool, "down": bool}, ...}
        """
        # Pohyb pálek (dočasná jednoduchá implementace)
        for pid, paddle in self.paddles.items():
            player_inp = inputs.get(pid, {})
            if player_inp.get("up"):
                paddle.y -= paddle.speed
            if player_inp.get("down"):
                paddle.y += paddle.speed
            # Omezit na arénu
            if paddle.y < 0:
                paddle.y = 0
            if paddle.y + paddle.height > self.arena.height:
                paddle.y = self.arena.height - paddle.height

        # Pohyb míčku (velmi jednoduchý placeholder)
        self.ball.x += self.ball.vx
        self.ball.y += self.ball.vy

        # Odraz od horní / dolní stěny
        if self.ball.y - self.ball.radius < 0 or self.ball.y + self.ball.radius > self.arena.height:
            self.ball.vy = -self.ball.vy

        # Odraz od levé / pravé stěny (zatím bez skóre)
        if self.ball.x - self.ball.radius < 0 or self.ball.x + self.ball.radius > self.arena.width:
            self.ball.vx = -self.ball.vx

        # Jednoduchá kolize s pálkami (pouze horizontální odraz)
        left = self.paddles.get("A1")
        right = self.paddles.get("B1")
        if left and (self.ball.x - self.ball.radius < left.x + left.width and left.y < self.ball.y < left.y + left.height):
            self.ball.vx = abs(self.ball.vx)
        if right and (self.ball.x + self.ball.radius > right.x and right.y < self.ball.y < right.y + right.height):
            self.ball.vx = -abs(self.ball.vx)
    
    def update_paddles(self, inputs: Dict[str, Dict[str, bool]]) -> None:
        """
        Aktualizuje pozice pálek podle vstupů.
        
        Args:
            inputs: Vstupy od hráčů
        """
        # TODO: Implementovat aktualizaci pálek
        pass
    
    def update_ball(self) -> None:
        """Aktualizuje pozici a rychlost míčku."""
        # TODO: Implementovat pohyb míčku
        pass
    
    def check_collisions(self) -> None:
        """Kontroluje a zpracovává všechny kolize."""
        # TODO: Implementovat detekci kolizí míček-pálka
        # TODO: Implementovat odraz od stěn
        pass
    
    def check_goals(self) -> Optional[str]:
        """
        Kontroluje, zda byl vstřelen gól.
        
        Returns:
            "A" nebo "B" pro tým, který dostal gól, None jinak
        """
        # TODO: Implementovat detekci gólu
        pass
    
    def score_goal(self, scoring_team: str) -> None:
        """
        Zaznamená gól pro daný tým.
        
        Args:
            scoring_team: Tým, který dal gól ("A" nebo "B")
        """
        # TODO: Implementovat přičtení gólu
        pass
    
    def reset_ball(self) -> None:
        """Resetuje míček do středu arény."""
        # TODO: Implementovat reset míčku
        pass
    
    def start(self) -> None:
        """Spustí hru."""
        self.is_running = True
        self.reset_ball()
    
    def stop(self) -> None:
        """Zastaví hru."""
        self.is_running = False
    
    def reset(self) -> None:
        """Resetuje hru do výchozího stavu."""
        # TODO: Implementovat reset hry
        pass
    
    def get_state(self) -> Dict:
        """
        Vrátí kompletní stav hry jako slovník (pro synchronizaci).
        
        Returns:
            Slovník s kompletním stavem hry
        """
        return {
            "ball": self.ball.to_dict(),
            "paddles": {
                pid: paddle.to_dict() 
                for pid, paddle in self.paddles.items()
            },
            "score": self.score.copy(),
            "time_left": self.time_left,
            "is_running": self.is_running,
            "arena": self.arena.to_dict()
        }
    
    def add_paddle(self, player_id: str, team: str, position: int) -> None:
        """
        Přidá novou pálku do hry (pro multiplayer 4v4).
        
        Args:
            player_id: ID hráče (např. "A2", "B3")
            team: Tým ("A" nebo "B")
            position: Pozice na ose Y
        """
        # TODO: Implementovat přidání pálky
        pass
    
    def remove_paddle(self, player_id: str) -> None:
        """
        Odebere pálku ze hry.
        
        Args:
            player_id: ID hráče
        """
        # TODO: Implementovat odebrání pálky
        pass
    
    def draw(self, surface) -> None:
        """Dočasné vykreslení stavu hry (placeholder)."""
        # Import uvnitř metody, aby engine zůstal použitelny bez Pygame
        try:
            import pygame  # type: ignore
        except ImportError:  # pragma: no cover - pokud pygame není dostupný
            return

        # Pozadí
        surface.fill((30, 30, 30))

        # Pálky
        for paddle in self.paddles.values():
            pygame.draw.rect(
                surface,
                (200, 200, 200),
                (int(paddle.x), int(paddle.y), int(paddle.width), int(paddle.height))
            )

        # Míček
        pygame.draw.circle(
            surface,
            (200, 80, 80),
            (int(self.ball.x), int(self.ball.y)),
            int(self.ball.radius)
        )

        # Jednoduché skóre (text)
        font = pygame.font.SysFont("consolas", 24)
        score_text = font.render(f"A {self.score['A']} : {self.score['B']} B", True, (220, 220, 220))
        surface.blit(score_text, (self.arena.width // 2 - score_text.get_width() // 2, 20))

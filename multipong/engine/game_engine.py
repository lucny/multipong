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
    
    def update(self, inputs: Optional[Dict[str, Dict[str, bool]]] = None) -> None:
        """Aktualizační smyčka enginu.

        Pokud nejsou předány vstupy (inputs is None), pokusí se přečíst stav klávesnice
        přes pygame (W/S pro levou pálku, šipky nahoru/dolů pro pravou). To vnáší
        závislost na pygame – tolerováno ve Phase 1–2.
        """
        # Volitelný vstup z pygame
        if inputs is None:
            try:  # pragma: no cover - přístup k reálné klávesnici mimo testy
                import pygame
                keys = pygame.key.get_pressed()
                inputs = {
                    "A1": {"up": keys[pygame.K_w], "down": keys[pygame.K_s]},
                    "B1": {"up": keys[pygame.K_UP], "down": keys[pygame.K_DOWN]},
                }
            except Exception:
                inputs = {"A1": {"up": False, "down": False}, "B1": {"up": False, "down": False}}

        # Pohyb pálek pomocí metod Paddle
        for pid, paddle in self.paddles.items():
            player_inp = inputs.get(pid, {}) if inputs else {}
            if player_inp.get("up"):
                paddle.move_up()
            if player_inp.get("down"):
                paddle.move_down()
            paddle.update(self.arena.height)

        # Pohyb míčku – využij vnitřní logiku Ball.update pro vertikální odrazy
        self.ball.update()

        # Horizontální odraz od levé / pravé stěny (zatím bez skórování)
        if self.ball.x - self.ball.radius < 0:
            self.ball.x = self.ball.radius
            self.ball.reverse_x()
        elif self.ball.x + self.ball.radius > self.arena.width:
            self.ball.x = self.arena.width - self.ball.radius
            self.ball.reverse_x()

        # Kolize míček–pálka (axis-aligned bounding box vs. kruh zjednodušeně):
        left = self.paddles.get("A1")
        if left and self._ball_hits_paddle(left):
            # Ujisti se, že míček se po odrazu pohybuje doprava
            self.ball.vx = abs(self.ball.vx)
            # Posuň míček ven z pálky, aby nedošlo k vícenásobnému odrazu
            self.ball.x = left.x + left.width + self.ball.radius

        right = self.paddles.get("B1")
        if right and self._ball_hits_paddle(right):
            self.ball.vx = -abs(self.ball.vx)
            self.ball.x = right.x - self.ball.radius

    def _ball_hits_paddle(self, paddle: Paddle) -> bool:
        """Jednoduchá detekce kolize míčku s pálkou.

        Aproximace: testujeme zda horizontální projekce kruhu zasahuje obdélník a
        střed míčku leží ve vertikálním rozsahu pálky.
        """
        return (
            paddle.y <= self.ball.y <= paddle.y + paddle.height and
            self.ball.x + self.ball.radius >= paddle.x and
            self.ball.x - self.ball.radius <= paddle.x + paddle.width
        )
    
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
        """Reset míčku do středu arény + základní rychlost zachována."""
        cx, cy = self.arena.get_center()
        self.ball.x = cx
        self.ball.y = cy
    
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

"""
MultipongEngine - Hlavní herní engine pro MULTIPONG
Logické jádro hry - nezávislé na Pygame.
"""

from typing import Dict, Optional, List
from .ball import Ball
from .paddle import Paddle
from .arena import Arena
from .player_stats import PlayerStats
from .team import Team
from .goal_zone import GoalZone
from multipong import settings


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
        team_left: Levý tým (Team instance) - původně team_a
        team_right: Pravý tým (Team instance) - původně team_b
        paddles: Slovník pálek {player_id: Paddle} (zpětná kompatibilita)
        score: Slovník skóre {"A": int, "B": int} (zpětná kompatibilita)
        goal_left: Branka vlevo (GoalZone)
        goal_right: Branka vpravo (GoalZone)
        is_running: Zda hra běží
    """
    
    def __init__(self, arena_width: int = 1200, arena_height: int = 800, num_players_per_team: int = 1):
        """
        Inicializace herního enginu.
        
        Args:
            arena_width: Šířka arény
            arena_height: Výška arény
            num_players_per_team: Počet hráčů na tým (1-4)
        """
        # Herní objekty
        self.arena = Arena(arena_width, arena_height)
        center_x, center_y = self.arena.get_center()
        self.ball = Ball(center_x, center_y)
        
        # Počet hráčů na tým
        self.num_players_per_team = max(1, min(4, num_players_per_team))
        
        # Týmy (Phase 3 architektura s názvy z dokumentace)
        self.team_left: Team = self._create_team("A", is_left=True)
        self.team_right: Team = self._create_team("B", is_left=False)
        
        # Aliasy pro zpětnou kompatibilitu
        self.team_a = self.team_left
        self.team_b = self.team_right
        
        # Zpětná kompatibilita - slovník pálek pro starý přístup
        self.paddles: Dict[str, Paddle] = {}
        for paddle in self.team_left.paddles + self.team_right.paddles:
            self.paddles[paddle.player_id] = paddle
        
        # Zpětná kompatibilita - skóre jako dict
        self.score = {"A": 0, "B": 0}
        
        # Branky (GoalZone) – výška z konfigurace
        goal_size = settings.GOAL_SIZE
        self.goal_left = GoalZone(
            x=0,
            top=arena_height // 2 - goal_size // 2,
            bottom=arena_height // 2 + goal_size // 2
        )
        self.goal_right = GoalZone(
            x=arena_width,
            top=arena_height // 2 - goal_size // 2,
            bottom=arena_height // 2 + goal_size // 2
        )
        
        # Stav hry
        self.is_running = False
        self.time_left = 120.0  # sekund
        # Pauza po gólu
        self.goal_pause_until: Optional[float] = None
        self._pending_ball_reset: bool = False
        self._last_ball_vx: float = self.ball.vx
        self._last_ball_vy: float = self.ball.vy
        # Telemetrie výměny (rally) – počet zásahů od posledního gólu
        self.rally_hits: int = 0
    
    def _create_team(self, name: str, is_left: bool) -> Team:
        """Vytvoří tým s pálkami.
        
        Args:
            name: Název týmu ("A" nebo "B")
            is_left: True pro levý tým, False pro pravý
            
        Returns:
            Instance Team se všemi pálkami
        """
        paddles: List[Paddle] = []
        zone_height = self.arena.height // self.num_players_per_team
        
        for i in range(self.num_players_per_team):
            player_id = f"{name}{i + 1}"
            
            # Per-slot výška pálky (fallback na PADDLE_HEIGHT)
            paddle_height = settings.PADDLE_HEIGHTS.get(player_id, settings.PADDLE_HEIGHT)
            
            # Pokud je výška 0, tento slot se neinicializuje
            if paddle_height <= 0:
                continue
            
            stats = PlayerStats(player_id)
            
            # Zóny pro vertikální rozdělení
            zone_top = i * zone_height
            zone_bottom = zone_top + zone_height
            
            # X-pozice podle strany a indexu
            if is_left:
                x = 50 + (i * 100)  # 50, 150, 250, 350
            else:
                x = self.arena.width - 70 - (i * 100)  # Zrcadlově zprava
            
            # Y-pozice na střed zóny
            y = zone_top + zone_height // 2 - 50  # -50 je polovina výšky pálky

            paddle = Paddle(
                x=x,
                y=y,
                height=paddle_height,
                player_id=player_id,
                zone_top=zone_top,
                zone_bottom=zone_bottom,
                stats=stats
            )
            paddles.append(paddle)
        
        return Team(name, paddles)
    
    def _initialize_paddles(self) -> None:
        """Inicializuje základní pálky pro 1v1 (deprecated - používá se _create_team)."""
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
        """Aktualizační smyčka enginu podle Phase 3 specifikace.

        Args:
            inputs: Slovník vstupů od hráčů {"A1": {"up": bool, "down": bool}, ...}.
                    Pokud je None, použije se prázdný slovník (žádné vstupy).
        """
        # Výchozí prázdné vstupy (paddle_inputs v dokumentaci)
        paddle_inputs = inputs if inputs is not None else {}

        # --- pohyb pálek --- (iterace přes oba týmy)
        unrestricted = settings.PADDLES_UNRESTRICTED_Y
        for team in [self.team_left, self.team_right]:
            for paddle in team.paddles:
                pid = paddle.stats.player_id  # Použij player_id ze stats
                if pid in paddle_inputs:  # Manuální vstup hráče
                    if paddle_inputs[pid].get("up"):
                        paddle.move_up()
                    if paddle_inputs[pid].get("down"):
                        paddle.move_down()
                else:  # Jednoduché AI pro volné pálky (vynecháme primární sloty A1/B1 kvůli testům)
                    if not pid.endswith("1"):
                        self._ai_control(paddle)
                paddle.update(self.arena.height, unrestricted=unrestricted)

        # Zpracování pauzy po gólu – pokud probíhá, zastavíme míček
        if self.goal_pause_until is not None:
            import time
            remaining = self.goal_pause_until - time.monotonic()
            if remaining <= 0:
                # Konec pauzy – uvedeme míček do hry
                self.goal_pause_until = None
                if self._pending_ball_reset:
                    self._serve_ball_after_pause()
            else:
                # Pauza aktivní – neprovádíme pohyb míčku ani kolize / góly
                return

        # --- pohyb míče --- (jen mimo pauzu)
        self.ball.update()
        # -----------------------------------
        #  ODRAZ OD ZADNÍCH STĚN MIMO BRANKY
        # -----------------------------------

        # Levá zadní stěna
        if self.ball.x - self.ball.radius <= 0:
            # pokud není v brankovém intervalu → odraz
            if not (self.goal_left.top <= self.ball.y <= self.goal_left.bottom):
                self.ball.x = self.ball.radius
                self.ball.reverse_x()

        # Pravá zadní stěna
        if self.ball.x + self.ball.radius >= self.arena.width:
            if not (self.goal_right.top <= self.ball.y <= self.goal_right.bottom):
                self.ball.x = self.arena.width - self.ball.radius
                self.ball.reverse_x()

        # --- kolize s pálkami --- (vylepšené – žádné "zasekávání") 
        collision_handled = False
        for team in [self.team_left, self.team_right]:
            if collision_handled:
                break

            for paddle in team.paddles:
                if not self._check_paddle_collision(paddle):
                    continue

                # 1) Povol jen "čelní" kolizi:
                #    - levý tým: míček se musí pohybovat doleva (vx < 0)
                #    - pravý tým: míček se musí pohybovat doprava (vx > 0)
                if team is self.team_left and self.ball.vx >= 0:
                    # míček letí od pálky, kolizi ignorujeme
                    continue
                if team is self.team_right and self.ball.vx <= 0:
                    continue

                # 2) Zaznamenej zásah + vizuální efekt
                paddle.stats.record_hit()
                paddle.apply_hit_effect()

                # 3) Přisazení míčku ven z pálky, aby nezůstal "uvnitř"
                if team is self.team_left:
                    # pálka je vlevo, míček má po odrazu letět doprava
                    self.ball.x = paddle.x + paddle.width + self.ball.radius
                else:
                    # pálka je vpravo, míček má po odrazu letět doleva
                    self.ball.x = paddle.x - self.ball.radius

                # 4) Skutečný odraz – invertuj vx
                self.ball.vx *= -1

                # Zrychlení míčku po odrazu (splňuje test očekávající nárůst rychlosti)
                self._increase_ball_speed()

                collision_handled = True
                break

        """         
        for team in [self.team_left, self.team_right]:
            for paddle in team.paddles:
                if self._check_paddle_collision(paddle):
                    paddle.stats.record_hit()
                    self.ball.vx *= -1
                    # Zrychli míček mírně po odrazu
                    # self._increase_ball_speed()
        """
        # --- pasivní zpomalení míčku proti exponenciálnímu růstu rychlosti ---
        self._apply_ball_speed_decay()

        # --- gól vlevo --- (míček proletěl levou branou -> bod pro pravý tým)
        if self.goal_left.check_goal(self.ball):
            self._handle_goal(scoring_team="B")

        # --- gól vpravo --- (míček proletěl pravou branou -> bod pro levý tým)
        if self.goal_right.check_goal(self.ball):
            self._handle_goal(scoring_team="A")

    def _ball_hits_paddle(self, paddle: Paddle) -> bool:
        """Jednoduchá detekce kolize míčku s pálkou (deprecated - použij _check_paddle_collision).

        Aproximace: testujeme zda horizontální projekce kruhu zasahuje obdélník a
        střed míčku leží ve vertikálním rozsahu pálky.
        """
        return self._check_paddle_collision(paddle)
    
    def _check_paddle_collision(self, paddle: Paddle) -> bool:
        """Detekce kolize míčku s pálkou podle Phase 3 specifikace.
        
        Rozšířeno o poloměr míčku pro přesnější detekci.
        
        Args:
            paddle: Instance pálky
            
        Returns:
            True pokud míček zasahuje pálku
        """
        # Horizontální překryv (včetně poloměru míčku)
        horizontal_overlap = (
            paddle.x - self.ball.radius <= self.ball.x <= paddle.x + paddle.width + self.ball.radius
        )
        # Vertikální překryv (včetně poloměru míčku)
        vertical_overlap = (
            paddle.y - self.ball.radius <= self.ball.y <= paddle.y + paddle.height + self.ball.radius
        )
        
        return horizontal_overlap and vertical_overlap

    def _increase_ball_speed(self) -> None:
        """Adaptivně zvýší rychlost míčku po odrazu od pálky.

        Přírůstek se zmenšuje s narůstající délkou výměny (rally_hits)
        podle RALLY_ADAPT_FACTOR. Pokud redukce >= 1 → žádné další zrychlení.
        Po aplikaci se rychlost omezí capem BALL_SPEED_MAX (pokud > 0).
        """
        base = settings.BALL_SPEED_INCREMENT
        if base <= 0:
            return
        if settings.RALLY_ADAPT_FACTOR > 0:
            reduction = self.rally_hits * settings.RALLY_ADAPT_FACTOR
            if reduction >= 1:
                return
            base = base * (1 - reduction)

        # Aplikace přírůstku dle směru komponent
        self.ball.vx += base if self.ball.vx >= 0 else -base
        self.ball.vy += base if self.ball.vy >= 0 else -base

        # Cap komponent rychlosti
        if settings.BALL_SPEED_MAX > 0:
            if abs(self.ball.vx) > settings.BALL_SPEED_MAX:
                self.ball.vx = settings.BALL_SPEED_MAX if self.ball.vx > 0 else -settings.BALL_SPEED_MAX
            if abs(self.ball.vy) > settings.BALL_SPEED_MAX:
                self.ball.vy = settings.BALL_SPEED_MAX if self.ball.vy > 0 else -settings.BALL_SPEED_MAX

    def _apply_ball_speed_decay(self) -> None:
        """Aplikuje separátní decay pro X a Y osu + zajišťuje rychlostní cap.

        Preferuje specifické BALL_SPEED_DECAY_X/Y pokud jsou v (0,1), jinak
        použije globální BALL_SPEED_DECAY. Po decayi aplikuje BALL_SPEED_MAX cap.
        """
        decay_x = settings.BALL_SPEED_DECAY_X if 0 < settings.BALL_SPEED_DECAY_X < 1 else settings.BALL_SPEED_DECAY
        decay_y = settings.BALL_SPEED_DECAY_Y if 0 < settings.BALL_SPEED_DECAY_Y < 1 else settings.BALL_SPEED_DECAY

        if 0 < decay_x < 1:
            self.ball.vx *= decay_x
        if 0 < decay_y < 1:
            self.ball.vy *= decay_y

        if settings.BALL_SPEED_MAX > 0:
            if abs(self.ball.vx) > settings.BALL_SPEED_MAX:
                self.ball.vx = settings.BALL_SPEED_MAX if self.ball.vx > 0 else -settings.BALL_SPEED_MAX
            if abs(self.ball.vy) > settings.BALL_SPEED_MAX:
                self.ball.vy = settings.BALL_SPEED_MAX if self.ball.vy > 0 else -settings.BALL_SPEED_MAX
    
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
        Kontroluje, zda byl vstřelen gól pomocí GoalZone.
        
        Returns:
            "A" nebo "B" pro tým, který dal gól, None jinak
        """
        # Míček proletěl levou branou -> gól pro pravý tým (B)
        if self.goal_left.check_goal(self.ball):
            return "B"
        # Míček proletěl pravou branou -> gól pro levý tým (A)
        elif self.goal_right.check_goal(self.ball):
            return "A"
        return None

    def check_score(self) -> None:
        """Zkontroluje gól a pokud nastal, zvýší skóre a resetuje míček."""
        scoring_team = self.check_goals()
        if scoring_team:
            self.score_goal(scoring_team)
    
    def score_goal(self, scoring_team: str) -> None:
        """
        Zaznamená gól pro daný tým (používá Team.add_score).
        
        Args:
            scoring_team: Tým, který dal gól ("A" nebo "B")
        """
        if scoring_team == "A":
            self.team_left.add_score()
            self.score["A"] = self.team_left.score  # Zpětná kompatibilita
        elif scoring_team == "B":
            self.team_right.add_score()
            self.score["B"] = self.team_right.score  # Zpětná kompatibilita
        
        self.reset_ball()

    def reset_ball(self) -> None:
        """Reset míčku do středu arény podle Phase 3 specifikace."""
        cx, cy = self.arena.get_center()
        self.ball.x = cx
        self.ball.y = cy
        # Invertuj směr míčku (podle dokumentace)
        self.ball.vx *= -1
        # Obnov výchozí rychlost (ztratí zrychlení z odrazů)
        self.ball.vx = settings.BALL_SPEED_X if self.ball.vx > 0 else -settings.BALL_SPEED_X
        self.ball.vy = settings.BALL_SPEED_Y if self.ball.vy > 0 else -settings.BALL_SPEED_Y
    
    def _reset_ball(self) -> None:
        """Interní reset míčku (alias pro reset_ball podle Phase 3)."""
        cx, cy = self.arena.get_center()
        self.ball.x = cx
        self.ball.y = cy
        # Invertuj směr vx (podle Phase 3 dokumentace)
        if self.ball.vx == 0:
            # Pokud je právě v pauze (vx=0), invertuj původní uložený směr
            self.ball.vx = -self._last_ball_vx
        else:
            self.ball.vx *= -1

    # ------------------------------------------------------------------
    # Nové pomocné metody (AI + pauza po gólu)
    # ------------------------------------------------------------------
    def _ai_control(self, paddle: Paddle) -> None:
        """Jednoduché AI: pálka sleduje vertikální pozici míčku.

        Pálka se snaží vycentrovat na míček v rámci své zóny.
        """
        target = self.ball.y - paddle.height / 2
        # Pokud je střed pálky pod cílem → posun nahoru / dolů
        if paddle.y < target:
            paddle.y += paddle.speed
        elif paddle.y > target:
            paddle.y -= paddle.speed

    def _handle_goal(self, scoring_team: str) -> None:
        """Ošetří gól: zvýší skóre, připraví pauzu před znovu-vhozením.

        Pauza: míček se zastaví uprostřed na 1s (konfigurovatelné)
        poté se znovu uvede do hry se stejným směrem vy (vx invertovaný).
        """
        import time
        # Zvýšení skóre
        if scoring_team == "A":
            self.team_left.add_score()
            self.score["A"] = self.team_left.score
        elif scoring_team == "B":
            self.team_right.add_score()
            self.score["B"] = self.team_right.score

        # Ulož poslední směr pro budoucí invertaci
        self._last_ball_vx = self.ball.vx if self.ball.vx != 0 else self._last_ball_vx
        self._last_ball_vy = self.ball.vy if self.ball.vy != 0 else self._last_ball_vy

        # Připrav míček do středu – zastavíme ho
        cx, cy = self.arena.get_center()
        self.ball.x = cx
        self.ball.y = cy
        self.ball.vx = 0
        self.ball.vy = 0

        # Nastav pauzu
        self.goal_pause_until = time.monotonic() + settings.GOAL_PAUSE_SECONDS
        self._pending_ball_reset = True
        # Reset výměny
        self.rally_hits = 0

    def _serve_ball_after_pause(self) -> None:
        """Uvede míček znovu do hry po pauze po gólu."""
        self._pending_ball_reset = False
        # Invertuj původní směr vx (jako _reset_ball) a obnov vy
        self.ball.vx = -self._last_ball_vx
        self.ball.vy = self._last_ball_vy

    def get_goal_pause_remaining(self) -> float:
        """Vrátí zbývající čas pauzy po gólu (sekundy)."""
        if self.goal_pause_until is None:
            return 0.0
        import time
        return max(0.0, self.goal_pause_until - time.monotonic())
    
    def start(self) -> None:
        """Spustí hru."""
        self.is_running = True
        self.reset_ball()
    
    def stop(self) -> None:
        """Zastaví hru."""
        self.is_running = False
    
    def reset(self) -> None:
        """Resetuje hru do výchozího stavu (míček, pálky, skóre, statistiky)."""
        # Reset skóre týmů (použij team_left/team_right)
        self.team_left.reset_score()
        self.team_right.reset_score()
        self.score = {"A": 0, "B": 0}
        
        # Reset statistik všech hráčů
        for paddle in self.team_left.paddles + self.team_right.paddles:
            paddle.stats.reset()
        
        # Reset míčku
        self.reset_ball()
        
        # Reset pálek na výchozí pozice
        for i, paddle in enumerate(self.team_left.paddles):
            zone_height = self.arena.height // self.num_players_per_team
            zone_top = i * zone_height
            paddle.y = zone_top + zone_height // 2 - paddle.height / 2
        
        for i, paddle in enumerate(self.team_right.paddles):
            zone_height = self.arena.height // self.num_players_per_team
            zone_top = i * zone_height
            paddle.y = zone_top + zone_height // 2 - paddle.height / 2
    
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
            "arena": self.arena.to_dict(),
            # Phase 3 rozšíření (podle dokumentace team_left/team_right)
            "team_left": self.team_left.to_dict(),
            "team_right": self.team_right.to_dict(),
            "goal_left": self.goal_left.to_dict(),
            "goal_right": self.goal_right.to_dict(),
            "goal_pause_remaining": self.get_goal_pause_remaining(),
            "rally_hits": self.rally_hits,
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

        # Vykreslení brankových zón (GoalZone) – jednoduché "sloupky"
        goal_color = (80, 160, 240)
        goal_width = 8
        # Levá branka
        pygame.draw.rect(
            surface,
            goal_color,
            pygame.Rect(
                0, int(self.goal_left.top),
                goal_width, int(self.goal_left.bottom - self.goal_left.top)
            ),
            border_radius=3,
        )
        # Pravá branka
        pygame.draw.rect(
            surface,
            goal_color,
            pygame.Rect(
                self.arena.width - goal_width, int(self.goal_right.top),
                goal_width, int(self.goal_right.bottom - self.goal_right.top)
            ),
            border_radius=3,
        )

        # Zvýraznění branky pokud je míček uvnitř vertikálního rozsahu
        if self.goal_left.top <= self.ball.y <= self.goal_left.bottom:
            pygame.draw.rect(
                surface,
                (120, 200, 255),
                pygame.Rect(0, int(self.goal_left.top), goal_width, int(self.goal_left.bottom - self.goal_left.top)),
                border_radius=3,
            )
        if self.goal_right.top <= self.ball.y <= self.goal_right.bottom:
            pygame.draw.rect(
                surface,
                (120, 200, 255),
                pygame.Rect(self.arena.width - goal_width, int(self.goal_right.top), goal_width, int(self.goal_right.bottom - self.goal_right.top)),
                border_radius=3,
            )

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

        # Pauza po gólu – zobraz odpočet
        if self.goal_pause_until is not None:
            remaining = self.get_goal_pause_remaining()
            pause_font = pygame.font.SysFont("consolas", 32)
            txt = pause_font.render(f"GOAL! Restart za {remaining:0.1f}s", True, (250, 210, 70))
            surface.blit(txt, (self.arena.width // 2 - txt.get_width() // 2, self.arena.height // 2 - 40))

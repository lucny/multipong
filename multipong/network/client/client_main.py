"""\nclient_main.py - Pygame klient pro MULTIPONG (lokální demo)\n\nTento soubor obsahuje jednoduchou Pygame smyčku, která:\n - inicializuje okno\n - vytvoří instanci MultipongEngine\n - ve smyčce zpracuje vstupy klávesnice\n - volá engine.update() a engine.draw()\n - vykreslí placeholder míček a pálky\n\nSíťová logika (WebSocket klient) je oddělena v `client.py`.\nZde zatím ignorujeme real-time server – čistě lokální demo.\n\nPoznámka: V první verzi je engine částečně svázán s Pygame skrze draw()\nmetodu. V pozdějších fázích bude vykreslování přesunuto do UI vrstvy.\n"""

from __future__ import annotations

import sys
import pathlib
import pygame
from typing import Dict

# Umožní spouštět tento skript přímo bez editable install
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]  # d:\projekty\multipong
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:  # Preferovaný import balíčku
    from multipong.engine import MultipongEngine
    from multipong.input.pygame_handler import PygameInputHandler
except ImportError:  # pragma: no cover - fallback při lokálním běhu
    from multipong.engine.game_engine import MultipongEngine  # type: ignore
    from multipong.input.pygame_handler import PygameInputHandler  # type: ignore

# Konstanta FPS
FPS = 60

# Barvy (placeholder)
COLOR_BACKGROUND = (30, 30, 30)


def main() -> None:
    """Spustí hlavní Pygame smyčku klienta."""
    pygame.init()

    # TESTOVACÍ REŽIM: pouze 1 hráč na tým (A1 vs B1)
    engine = MultipongEngine(arena_width=1200, arena_height=800, num_players_per_team=1)
    engine.start()

    # Vytvoř input handler (dependency injection)
    input_handler = PygameInputHandler()

    screen = pygame.display.set_mode((engine.arena.width, engine.arena.height))
    pygame.display.set_caption("MULTIPONG – Test Режim (A1 vs B1) – ESC=konec, R=reset")
    
    # Font pro zobrazení skóre
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 48)

    clock = pygame.time.Clock()

    running = True
    while running:
        # Události
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset hry
                    engine.reset()

        # Vstupy pomocí input handleru (dependency inversion)
        inputs = input_handler.get_inputs()

        # Logika
        engine.update(inputs)

        # Vykreslení
        engine.draw(screen)
        
        # Zobrazení skóre na obrazovce + případná pauza po gólu
        score_text = f"{engine.team_left.score} : {engine.team_right.score}"
        pause_remaining = engine.get_goal_pause_remaining() if hasattr(engine, "get_goal_pause_remaining") else 0.0
        if pause_remaining > 0:
            score_text += f"  (GOAL – restart za {pause_remaining:0.1f}s)"
        text_surface = font.render(score_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(engine.arena.width // 2, 50))
        screen.blit(text_surface, text_rect)
        
        # Zobrazení nápovědy
        help_font = pygame.font.SysFont("Arial", 20)
        help_text = "W/S = Levá pálka (team_left) | ↑/↓ = Pravá pálka (team_right) | R = Reset | ESC = Konec"
        help_surface = help_font.render(help_text, True, (180, 180, 180))
        help_rect = help_surface.get_rect(center=(engine.arena.width // 2, engine.arena.height - 30))
        screen.blit(help_surface, help_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":  # pragma: no cover
    try:
        main()
    except Exception as e:
        print(f"Chyba v klientu: {e}")
        pygame.quit()
        sys.exit(1)

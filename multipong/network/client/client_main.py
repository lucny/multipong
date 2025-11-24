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
except ImportError:  # pragma: no cover - fallback při lokálním běhu
    from multipong.engine.game_engine import MultipongEngine  # type: ignore

# Konstanta FPS
FPS = 60

# Barvy (placeholder)
COLOR_BACKGROUND = (30, 30, 30)


def gather_inputs() -> Dict[str, Dict[str, bool]]:
    """Sejme vstupy z klávesnice pro pálky.

    Vrací slovník ve formátu: {"A1": {"up": bool, "down": bool}, "B1": {...}}
    """
    keys = pygame.key.get_pressed()
    return {
        "A1": {
            "up": keys[pygame.K_w],
            "down": keys[pygame.K_s],
        },
        "B1": {
            "up": keys[pygame.K_UP],
            "down": keys[pygame.K_DOWN],
        },
    }


def main() -> None:
    """Spustí hlavní Pygame smyčku klienta."""
    pygame.init()

    # Rozměry z enginu (arénu vytvoříme nejdříve)
    engine = MultipongEngine(arena_width=1200, arena_height=800)
    engine.start()

    screen = pygame.display.set_mode((engine.arena.width, engine.arena.height))
    pygame.display.set_caption("MULTIPONG – Client Demo")

    clock = pygame.time.Clock()

    running = True
    while running:
        # Události
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Vstupy
        inputs = gather_inputs()

        # Logika
        engine.update(inputs)

        # Vykreslení (engine si pokryje vše v draw)
        engine.draw(screen)

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

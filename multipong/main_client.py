"""
main_client.py – síťový Pygame klient pro MULTIPONG (Phase 5)

- Připojí se k WS serveru
- Odesílá vstupy (nahoru/dolů)
- Přijímá snapshoty, ukládá je do StateBufferu a vykresluje přes Renderer

Spuštění:
  python -m multipong.main_client
nebo
  python multipong/main_client.py
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Optional, Dict

try:  # pragma: no cover - pygame nemusí být v CI
    import pygame
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

from multipong import settings
from multipong.network.client.ws_client import WSClient
from multipong.network.client.state_buffer import StateBuffer
from multipong.ui.renderer import Renderer


async def run_client(player_id: str = "auto", url: str = "ws://localhost:8000/ws") -> None:
    if not pygame:  # pragma: no cover
        print("Pygame není dostupný – nelze spustit renderer.")
        return

    pygame.init()
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    pygame.display.set_caption("MULTIPONG – Client")

    buffer = StateBuffer(max_size=3)
    renderer = Renderer(screen)

    # Latency tracking
    latency_ms = 0.0
    pending_pings: Dict[str, float] = {}  # {ping_id: timestamp}

    # Snapshot debug counter
    snapshot_count = 0

    # Při doručení snapshotu přidáme do bufferu
    def on_snapshot(msg: dict) -> None:
        nonlocal snapshot_count
        # Server posílá {type: "snapshot", ...state}
        state = dict(msg)
        state.pop("type", None)
        buffer.add_state(state)
        snapshot_count += 1

    # Volitelné callbacky
    def on_connected(info: dict) -> None:
        slot = info.get("assigned_slot")
        print(f"Připojeno. Přidělený slot: {slot}")

    def on_chat(sender: str, message: str) -> None:
        print(f"[{sender}] {message}")

    def on_pong(data: dict) -> None:
        nonlocal latency_ms
        ping_id = data.get("ping_id")
        if ping_id and ping_id in pending_pings:
            sent_time = pending_pings.pop(ping_id)
            latency_ms = (asyncio.get_event_loop().time() - sent_time) * 1000

    client = WSClient(url=url, player_id=player_id, on_snapshot=on_snapshot, on_connected=on_connected, on_chat=on_chat, on_pong=on_pong)
    ok = await client.connect()
    if not ok:
        print("Nepodařilo se připojit k serveru.")
        pygame.quit()
        return

    # Asynchronní smyčka – neblokujeme event loop pomocí pygame.Clock.tick
    running = True
    frame_interval = 1.0 / settings.DEFAULT_FPS
    last_ping = 0.0
    last_input_send = 0.0
    input_send_interval = 1.0 / 20.0  # Limit input sends to ~20 Hz

    try:
        while running:
            # Zpracování Pygame událostí (blokující část je krátká)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            keys = pygame.key.get_pressed()
            up = bool(keys[pygame.K_UP] or keys[pygame.K_w])
            down = bool(keys[pygame.K_DOWN] or keys[pygame.K_s])

            # Odeslat vstupy – pokud spojení stále aktivní a jsme pod throttle limitou
            now = asyncio.get_event_loop().time()
            if client.is_connected() and (now - last_input_send) > input_send_interval:
                # Neblokovat hlavní smyčku při síťovém send – spustit jako task
                asyncio.create_task(client.send_input(up=up, down=down))
                last_input_send = now
            elif not client.is_connected():
                # Pokud klient odpojen – pokus o reconnection (jednoduché)
                recon_ok = await client.connect()
                if not recon_ok:
                    await asyncio.sleep(1.0)
                    continue

            # Periodický ping každých ~5s pro keep-alive a budoucí latency metriku
            if now - last_ping > 5.0 and client.is_connected():
                ping_id = str(uuid.uuid4())
                pending_pings[ping_id] = now
                asyncio.create_task(client.send_ping(ping_id=ping_id))
                last_ping = now

            # Interpolovaný stav – fallback na latest
            interp = buffer.get_interpolated() or buffer.get_latest()
            if interp:
                renderer.draw(interp)
                
                # Vykresli debug overlay (latency, snapshot count, buffer size)
                small_font = pygame.font.SysFont("consolas", 14)
                debug_texts = [
                    f"Latency: {latency_ms:.1f}ms",
                    f"Snapshots: {snapshot_count}",
                    f"Buffer: {buffer.size()}"
                ]
                for i, text in enumerate(debug_texts):
                    txt = small_font.render(text, True, (100, 200, 100))
                    pygame.display.get_surface().blit(txt, (10, 10 + i * 18))
                pygame.display.flip()
            else:
                # Jednoduchý text "Waiting for snapshot"
                pygame.display.get_surface().fill((0,0,0))
                f = pygame.font.SysFont("consolas", 24)
                txt = f.render("Waiting for snapshot...", True, (200,200,200))
                pygame.display.get_surface().blit(txt, (40,40))
                pygame.display.flip()

            # Uvolni event loop pro příjem snapshotů
            await asyncio.sleep(frame_interval)
    finally:
        await client.disconnect()
        pygame.quit()


def main() -> None:  # pragma: no cover
    import sys
    # Použití: python -m multipong.main_client [player_id] [server_url]
    player_id = "auto"
    url = "ws://localhost:8000/ws"
    if len(sys.argv) > 1 and sys.argv[1]:
        player_id = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2]:
        url = sys.argv[2]
    asyncio.run(run_client(player_id=player_id, url=url))


if __name__ == "__main__":  # pragma: no cover
    main()

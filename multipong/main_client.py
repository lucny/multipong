"""
main_client.py – síťový Pygame klient pro MULTIPONG (Phase 12)

- Úvodní menu (Multiplayer/Local/Settings/Quit)
- Lobby systém (výběr slotu, týmy, ready states)
- Countdown před zápasem
- Připojení k WS serveru a odesílání vstupů
- Přijímá snapshoty, ukládá je do StateBufferu a vykresluje přes Renderer

Spuštění:
  python -m multipong.main_client
nebo
  python multipong/main_client.py
"""

from __future__ import annotations

import asyncio
import uuid
import time
from typing import Optional, Dict

try:  # pragma: no cover - pygame nemusí být v CI
    import pygame
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

from multipong import settings
from multipong.network.client.ws_client import WSClient
from multipong.network.client.state_buffer import StateBuffer
from multipong.ui.renderer import Renderer
from multipong.client.ui.menu import MenuUI, LobbyUI, CountdownUI, GameState


async def run_client(player_id: str = "auto", url: str = "ws://localhost:8000/ws") -> None:
    if not pygame:  # pragma: no cover
        print("Pygame není dostupný – nelze spustit renderer.")
        return

    pygame.init()
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    pygame.display.set_caption("MULTIPONG")

    buffer = StateBuffer(max_size=3)
    renderer = Renderer(screen)

    # UI components
    menu_ui = MenuUI(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
    lobby_ui = LobbyUI(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
    countdown_ui = CountdownUI(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
    
    # State management
    game_state = GameState.MENU
    
    # Player info
    my_player_name = player_id if player_id != "auto" else f"Player_{uuid.uuid4().hex[:6]}"
    my_slot: Optional[str] = None
    my_ready = False
    
    # Countdown tracking
    countdown_start_time: Optional[float] = None
    countdown_duration = 3  # seconds

    # Latency tracking
    latency_ms = 0.0
    pending_pings: Dict[str, float] = {}  # {ping_id: timestamp}

    # Snapshot debug counter
    snapshot_count = 0
    
    # WebSocket client (initially None)
    client: Optional[WSClient] = None

    
    # Setup fonts first
    menu_ui.setup_fonts()
    lobby_ui.setup_fonts()
    countdown_ui.setup_fonts()
    
    # Define callbacks BEFORE setup_buttons
    def on_multiplayer_click():
        nonlocal game_state, client
        print("🌐 Connecting to multiplayer server...")
        game_state = GameState.LOBBY
        # Create WebSocket connection
        asyncio.create_task(connect_to_server())
    
    def on_local_click():
        nonlocal game_state
        print("🏠 Starting local game...")
        game_state = GameState.GAME
        # TODO: Start local game without server
    
    def on_settings_click():
        print("⚙️ Settings (not implemented yet)")
    
    def on_quit_click():
        nonlocal running
        print("👋 Quit")
        running = False
    
    # Assign callbacks to menu_ui
    menu_ui.on_multiplayer = on_multiplayer_click
    menu_ui.on_local = on_local_click
    menu_ui.on_settings = on_settings_click
    menu_ui.on_quit = on_quit_click
    
    # Now create buttons with callbacks already set
    menu_ui.setup_buttons()
    
    # Lobby callbacks - set before setup_slot_buttons
    def on_choose_slot(slot: str):
        nonlocal my_slot
        print(f"🎯 Choosing slot {slot}")
        my_slot = slot
        lobby_ui.my_slot = slot
        if client and client.is_connected():
            asyncio.create_task(client.send_message({"type": "choose_slot", "slot": slot}))
    
    def on_set_ready(is_ready: bool):
        nonlocal my_ready
        print(f"✓ Setting ready: {is_ready}")
        my_ready = is_ready
        if client and client.is_connected():
            asyncio.create_task(client.send_message({"type": "set_ready", "ready": is_ready}))
    
    lobby_ui.on_choose_slot = on_choose_slot
    lobby_ui.on_set_ready = on_set_ready
    
    # Now create lobby slot buttons
    lobby_ui.setup_slot_buttons()
    
    # WebSocket connection function
    async def connect_to_server():
        nonlocal client
        
        # Při doručení snapshotu přidáme do bufferu
        def on_snapshot(msg: dict) -> None:
            nonlocal snapshot_count
            state = dict(msg)
            state.pop("type", None)
            buffer.add_state(state)
            snapshot_count += 1

        # Volitelné callbacky
        def on_connected(info: dict) -> None:
            slot = info.get("assigned_slot")
            print(f"✓ Connected. Assigned slot: {slot}")
            # Join lobby
            if client:
                asyncio.create_task(client.send_message({"type": "join_lobby", "player_name": my_player_name}))

        def on_chat(sender: str, message: str) -> None:
            print(f"[{sender}] {message}")

        def on_pong(data: dict) -> None:
            nonlocal latency_ms
            ping_id = data.get("ping_id")
            if ping_id and ping_id in pending_pings:
                sent_time = pending_pings.pop(ping_id)
                latency_ms = (asyncio.get_event_loop().time() - sent_time) * 1000
        
        def on_message(msg: dict) -> None:
            nonlocal game_state, countdown_start_time
            msg_type = msg.get("type")
            
            if msg_type == "lobby_update":
                # Update lobby UI
                lobby_ui.update_lobby_state(msg)
            
            elif msg_type == "start_match":
                # Start countdown
                print("🎮 Starting match!")
                game_state = GameState.COUNTDOWN
                countdown_start_time = time.time()
        
        client = WSClient(
            url=url,
            player_id=my_player_name,
            on_snapshot=on_snapshot,
            on_connected=on_connected,
            on_chat=on_chat,
            on_pong=on_pong,
            on_message=on_message
        )
        ok = await client.connect()
        if not ok:
            print("❌ Failed to connect to server")
            game_state = GameState.MENU

    # Při doručení snapshotu přidáme do bufferu
    
    # Original callbacks (now moved into connect_to_server)
    """
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
    """

    # Asynchronní smyčka – neblokujeme event loop pomocí pygame.Clock.tick
    running = True
    frame_interval = 1.0 / settings.DEFAULT_FPS
    last_ping = 0.0
    last_input_send = 0.0
    input_send_interval = 1.0 / 20.0  # Limit input sends to ~20 Hz

    try:
        while running:
            # Zpracování Pygame událostí
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if game_state == GameState.GAME:
                        # ESC v hře -> zpět do lobby/menu
                        game_state = GameState.LOBBY
                    elif game_state == GameState.LOBBY:
                        # ESC v lobby -> zpět do menu
                        game_state = GameState.MENU
                        if client:
                            asyncio.create_task(client.disconnect())
                            client = None
                    else:
                        running = False
                
                # Pass events to UI components
                if game_state == GameState.MENU:
                    menu_ui.handle_event(event)
                elif game_state == GameState.LOBBY:
                    lobby_ui.handle_event(event)
            
            # Handle countdown -> game transition
            if game_state == GameState.COUNTDOWN and countdown_start_time:
                elapsed = time.time() - countdown_start_time
                if elapsed >= countdown_duration:
                    print("🎮 GO! Starting game...")
                    game_state = GameState.GAME
                    countdown_start_time = None

            # Game state logic
            if game_state == GameState.GAME:
                keys = pygame.key.get_pressed()
                up = bool(keys[pygame.K_UP] or keys[pygame.K_w])
                down = bool(keys[pygame.K_DOWN] or keys[pygame.K_s])

                # Odeslat vstupy
                now = asyncio.get_event_loop().time()
                if client and client.is_connected() and (now - last_input_send) > input_send_interval:
                    asyncio.create_task(client.send_input(up=up, down=down))
                    last_input_send = now
                elif client and not client.is_connected():
                    # Reconnection attempt
                    recon_ok = await client.connect()
                    if not recon_ok:
                        await asyncio.sleep(1.0)
                        continue

                # Periodický ping
                if client and now - last_ping > 5.0 and client.is_connected():
                    ping_id = str(uuid.uuid4())
                    pending_pings[ping_id] = now
                    asyncio.create_task(client.send_ping(ping_id=ping_id))
                    last_ping = now

            # Render based on state
            screen.fill((0, 0, 0))
            
            if game_state == GameState.MENU:
                menu_ui.draw(screen)
            
            elif game_state == GameState.LOBBY:
                lobby_ui.draw(screen)
            
            elif game_state == GameState.COUNTDOWN:
                if countdown_start_time:
                    elapsed = time.time() - countdown_start_time
                    countdown_value = max(0, countdown_duration - int(elapsed))
                    countdown_ui.draw(screen, countdown_value)
            
            elif game_state == GameState.GAME:
                # Interpolovaný stav – fallback na latest
                interp = buffer.get_interpolated() or buffer.get_latest()
                if interp:
                    renderer.draw(interp)
                    
                    # Vykresli debug overlay
                    small_font = pygame.font.SysFont("consolas", 14)
                    debug_texts = [
                        f"Latency: {latency_ms:.1f}ms",
                        f"Snapshots: {snapshot_count}",
                        f"Buffer: {buffer.size()}",
                        f"Slot: {my_slot or 'N/A'}"
                    ]
                    for i, text in enumerate(debug_texts):
                        txt = small_font.render(text, True, (100, 200, 100))
                        screen.blit(txt, (10, 10 + i * 18))
                else:
                    # Waiting for snapshot
                    f = pygame.font.SysFont("consolas", 24)
                    txt = f.render("Waiting for snapshot...", True, (200, 200, 200))
                    screen.blit(txt, (40, 40))
            
            pygame.display.flip()

            # Uvolni event loop
            await asyncio.sleep(frame_interval)
    finally:
        if client:
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

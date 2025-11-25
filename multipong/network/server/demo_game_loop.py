"""
Demo příklad použití game_loop s MultipongEngine a WebSocketManager.
"""

import asyncio
import logging
from unittest.mock import AsyncMock
from multipong.engine.game_engine import MultipongEngine
from multipong.network.server.websocket_manager import WebSocketManager
from multipong.network.server.player_session import PlayerSession
from multipong.network.server.game_loop import GameLoop


# Konfigurace logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_game_loop():
    """Demonstrace běhu game loop s engine a manager."""
    
    print("=" * 70)
    print("Demo: Game Loop s MultipongEngine")
    print("=" * 70)
    
    # 1. Vytvoření enginu a manageru
    print("\n🎮 Inicializace komponenty...")
    engine = MultipongEngine(arena_width=1200, arena_height=800, num_players_per_team=2)
    manager = WebSocketManager()
    
    # 2. Simulace připojených hráčů (mock WebSockets)
    print("\n👥 Přidávání simulovaných hráčů...")
    mock_ws_a1 = AsyncMock()
    mock_ws_b1 = AsyncMock()
    
    session_a1 = PlayerSession(mock_ws_a1, "A1")
    session_b1 = PlayerSession(mock_ws_b1, "B1")
    
    await manager.add(session_a1)
    await manager.add(session_b1)
    
    print(f"   Připojeno hráčů: {manager.get_player_count()}")
    print(f"   Player IDs: {manager.get_player_ids()}")
    
    # 3. Vytvoření game loop
    print("\n⚙️  Vytváření game loop (tick rate: 30 Hz)...")
    game_loop = GameLoop(engine, manager, tick_rate=30)
    
    # 4. Simulace vstupů od hráčů
    print("\n⌨️  Nastavení vstupů od hráčů...")
    game_loop.update_input("A1", up=True, down=False)
    game_loop.update_input("B1", up=False, down=True)
    
    print(f"   Aktuální vstupy: {game_loop.get_current_inputs()}")
    
    # 5. Spuštění game loop na pozadí
    print("\n🚀 Spouštím game loop...")
    task = asyncio.create_task(game_loop.run())
    
    # 6. Nechá běžet 2 sekundy a sleduj broadcast
    print("\n📊 Game loop běží (2 sekundy)...")
    await asyncio.sleep(2.0)
    
    # Zkontroluj kolikrát byl volán broadcast
    broadcast_count = mock_ws_a1.send_json.call_count
    print(f"\n   📡 Broadcast volán {broadcast_count}× pro hráče A1")
    
    # Zobraz poslední snapshot
    if mock_ws_a1.send_json.called:
        last_snapshot = mock_ws_a1.send_json.call_args[0][0]
        print(f"\n   📦 Poslední snapshot:")
        print(f"      - Type: {last_snapshot.get('type')}")
        print(f"      - Score: {last_snapshot.get('score')}")
        print(f"      - Ball: x={last_snapshot.get('ball', {}).get('x'):.1f}, "
              f"y={last_snapshot.get('ball', {}).get('y'):.1f}")
    
    # 7. Změna vstupů za běhu
    print("\n⌨️  Měním vstupy (A1: down=True)...")
    game_loop.update_input("A1", up=False, down=True)
    await asyncio.sleep(1.0)
    
    # 8. Zastavení loop
    print("\n🛑 Zastavuji game loop...")
    game_loop.stop()
    
    # Počkej na ukončení tasku
    try:
        await asyncio.wait_for(task, timeout=2.0)
    except asyncio.TimeoutError:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    print(f"\n   ✅ Game loop zastaven")
    print(f"   📊 Finální stav:")
    print(f"      - Engine běží: {engine.is_running}")
    print(f"      - Připojených hráčů: {manager.get_player_count()}")
    
    # 9. Odpojení hráčů
    print("\n🔌 Odpojuji všechny hráče...")
    await manager.disconnect_all()
    
    print("\n" + "=" * 70)
    print("✅ Demo dokončeno!")
    print("=" * 70)


async def demo_functional_api():
    """Demonstrace funkčního API run_game_loop()."""
    
    print("\n" + "=" * 70)
    print("Demo: Funkční API run_game_loop()")
    print("=" * 70)
    
    from multipong.network.server.game_loop import run_game_loop
    
    # Příprava
    engine = MultipongEngine(arena_width=800, arena_height=600, num_players_per_team=1)
    manager = WebSocketManager()
    
    # Sdílená mapa vstupů
    player_inputs = {
        "A1": {"up": True, "down": False},
        "B1": {"up": False, "down": False}
    }
    
    # Mock WebSocket pro test
    mock_ws = AsyncMock()
    session = PlayerSession(mock_ws, "A1")
    await manager.add(session)
    
    print(f"\n🚀 Spouštím run_game_loop (30 Hz)...")
    
    # Spuštění na pozadí
    task = asyncio.create_task(
        run_game_loop(engine, manager, player_inputs, tick_rate=30)
    )
    
    # Běh
    print("📊 Loop běží (1 sekunda)...")
    await asyncio.sleep(1.0)
    
    # Změna vstupů za běhu (sdílená mapa)
    print("⌨️  Měním vstupy v player_inputs...")
    player_inputs["A1"]["down"] = True
    
    await asyncio.sleep(0.5)
    
    # Zastavení
    print("🛑 Zastavuji loop...")
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        print("✅ Loop zrušen")
    
    print(f"📡 Broadcast volán {mock_ws.send_json.call_count}×")
    
    await manager.disconnect_all()
    
    print("=" * 70)


if __name__ == "__main__":
    async def main():
        await demo_game_loop()
        await demo_functional_api()
    
    asyncio.run(main())

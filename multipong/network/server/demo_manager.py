"""
Ukázkový příklad použití PlayerSession a WebSocketManager.
"""

import asyncio
from unittest.mock import AsyncMock
from multipong.network.server.player_session import PlayerSession
from multipong.network.server.websocket_manager import WebSocketManager


async def demo_usage():
    """Demonstrace použití PlayerSession a WebSocketManager."""
    
    print("=" * 60)
    print("Demo: PlayerSession a WebSocketManager")
    print("=" * 60)
    
    # Vytvoření manageru
    manager = WebSocketManager()
    print(f"\n✅ Vytvořen manager: {manager}")
    
    # Simulace WebSocket připojení (v reálném použití by to byl skutečný WebSocket)
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    mock_ws3 = AsyncMock()
    
    # Vytvoření sessions
    session_a1 = PlayerSession(mock_ws1, "A1")
    session_a2 = PlayerSession(mock_ws2, "A2")
    session_b1 = PlayerSession(mock_ws3, "B1")
    
    print(f"\n✅ Vytvořeny sessions:")
    print(f"   - {session_a1}")
    print(f"   - {session_a2}")
    print(f"   - {session_b1}")
    
    # Přidání hráčů
    print(f"\n📥 Přidávám hráče do manageru...")
    await manager.add(session_a1)
    await manager.add(session_a2)
    await manager.add(session_b1)
    
    print(f"   Počet hráčů: {manager.get_player_count()}")
    print(f"   Player IDs: {manager.get_player_ids()}")
    
    # Aktualizace vstupů
    print(f"\n⌨️  Aktualizace vstupů od hráčů...")
    session_a1.update_input(up=True, down=False)
    session_a2.update_input(up=False, down=True)
    session_b1.update_input(up=True, down=True)
    
    # Sesbírání vstupů
    inputs = manager.collect_inputs()
    print(f"   Sesbírané vstupy:")
    for player_id, player_input in inputs.items():
        print(f"     {player_id}: {player_input}")
    
    # Broadcast zprávy všem
    print(f"\n📡 Broadcast zprávy všem hráčům...")
    message_all = {
        "type": "snapshot",
        "ball": {"x": 500, "y": 300},
        "score": {"A": 2, "B": 1}
    }
    sent_count = await manager.broadcast(message_all)
    print(f"   Odesláno {sent_count} hráčům")
    
    # Broadcast pouze týmu A
    print(f"\n📡 Broadcast pouze týmu A...")
    message_team_a = {
        "type": "team_message",
        "message": "Dobrá práce tým A!"
    }
    sent_count = await manager.broadcast_to_team(message_team_a, "A")
    print(f"   Odesláno {sent_count} hráčům z týmu A")
    
    # Broadcast s vyloučením
    print(f"\n📡 Broadcast všem kromě A1...")
    message_exclude = {
        "type": "announcement",
        "text": "Zpráva pro všechny kromě A1"
    }
    sent_count = await manager.broadcast(message_exclude, exclude=["A1"])
    print(f"   Odesláno {sent_count} hráčům")
    
    # Získání konkrétní session
    print(f"\n🔍 Hledání session pro hráče B1...")
    session = manager.get_session("B1")
    if session:
        print(f"   Nalezena session: {session}")
        print(f"   Aktuální input: {session.get_input()}")
    
    # Odebrání hráče
    print(f"\n📤 Odebírám hráče A2...")
    await manager.remove_by_id("A2")
    print(f"   Zbývající hráči: {manager.get_player_ids()}")
    print(f"   Počet hráčů: {manager.get_player_count()}")
    
    # Odpojení všech
    print(f"\n🔌 Odpojuji všechny hráče...")
    await manager.disconnect_all()
    print(f"   Počet hráčů: {manager.get_player_count()}")
    print(f"   Manager: {manager}")
    
    print("\n" + "=" * 60)
    print("✅ Demo dokončeno!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo_usage())

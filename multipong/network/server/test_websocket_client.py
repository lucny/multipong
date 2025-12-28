"""
Testovací klient pro MULTIPONG WebSocket server.
Odesílá testovací zprávy a kontroluje, zda server přijímá.
"""

import asyncio
import json
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed


async def test_websocket():
    """Testovací funkce pro WebSocket spojení."""
    uri = "ws://localhost:8000/ws/TEST_PLAYER"
    
    print("🔌 Připojuji se k serveru...")
    
    try:
        async with connect(uri) as websocket:
            print("✅ Připojeno!")
            
            # Test 1: Input zpráva
            print("\n📤 Odesílám input zprávu...")
            input_msg = {
                "type": "input",
                "player_id": "TEST_PLAYER",
                "up": True,
                "down": False
            }
            await websocket.send(json.dumps(input_msg))
            print(f"   Odesláno: {input_msg}")
            
            # Krátké čekání
            await asyncio.sleep(0.5)
            
            # Test 2: Ping zpráva
            print("\n📤 Odesílám ping zprávu...")
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            print(f"   Odesláno: {ping_msg}")
            
            await asyncio.sleep(0.5)
            
            # Test 3: Chat zpráva
            print("\n📤 Odesílám chat zprávu...")
            chat_msg = {
                "type": "chat",
                "message": "Hello from test client!"
            }
            await websocket.send(json.dumps(chat_msg))
            print(f"   Odesláno: {chat_msg}")
            
            await asyncio.sleep(0.5)
            
            # Test 4: Neznámý typ zprávy
            print("\n📤 Odesílám neznámou zprávu...")
            unknown_msg = {
                "type": "unknown_type",
                "data": "test"
            }
            await websocket.send(json.dumps(unknown_msg))
            print(f"   Odesláno: {unknown_msg}")
            
            await asyncio.sleep(0.5)
            
            print("\n✅ Všechny zprávy odeslány!")
            print("💡 Zkontroluj server log pro potvrzení příjmu.")
            
    except ConnectionClosed:
        print("❌ Spojení ukončeno serverem")
    except ConnectionRefusedError:
        print("❌ Server není dostupný na ws://localhost:8000")
        print("   Spusť server příkazem:")
        print("   uvicorn multipong.network.server.websocket_server:app")
    except Exception as e:
        print(f"❌ Chyba: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🏓 MULTIPONG WebSocket Server - Test Client")
    print("=" * 60)
    asyncio.run(test_websocket())
    print("\n" + "=" * 60)

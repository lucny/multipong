"""
Demo skript pro testování lobby systému, timeoutu a chat funkcionalit.
Spustí WebSocket server a umožní otestovat všechny tři výzvy z Phase 4.
"""

import asyncio
import logging
from multipong.network.server import app, manager, lobby

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def print_lobby_status():
    """Periodicky vypisuje stav lobby."""
    while True:
        await asyncio.sleep(5)
        status = lobby.get_lobby_status()
        logger.info(f"📊 Lobby Status:")
        logger.info(f"   Volné pozice: {status['available']}")
        logger.info(f"   Obsazené: {status['occupied']}")
        logger.info(f"   Celkem hráčů: {status['players_count']}/{status['total_slots']}")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════╗
║      🏓 MULTIPONG WebSocket Server - Phase 4 Výzvy Demo     ║
╚═══════════════════════════════════════════════════════════════╝

Implementované funkce:

🔹 1) TIMEOUT - Automatické odpojení neaktivních hráčů
   • Hráči, kteří 10 sekund nepošlou žádnou zprávu, jsou odpojeni
   • Kontrola probíhá každých 5 sekund
   
🔹 2) LOBBY SYSTÉM - Automatické přidělování pozic
   • Připoj se s player_id="auto" pro automatické přidělení
   • Nebo zadej konkrétní pozici: "A1", "A2", "B1", atd.
   • Neaktivní pozice (A2, B3 - height=0) jsou přeskočeny
   
🔹 3) CHAT ZPRÁVY - Broadcast komunikace
   • Poslat: {"type": "chat", "message": "Hello!"}
   • Zpráva je rozeslána všem připojeným hráčům

════════════════════════════════════════════════════════════════

🌐 Server běží na: http://localhost:8000
📱 Test klient: http://localhost:8000/test-client
🔍 Lobby status: http://localhost:8000/lobby/status

WebSocket endpoint:
   ws://localhost:8000/ws/{player_id}
   nebo
   ws://localhost:8000/ws/auto  (automatické přidělení)

════════════════════════════════════════════════════════════════

Pro ukončení serveru stiskněte Ctrl+C

════════════════════════════════════════════════════════════════
    """)
    
    # Spustíme server
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

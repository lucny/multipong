"""
Demo WebSocket klient - test připojení k MULTIPONG serveru.
Konzolová aplikace pro testování WSClient.
"""

import asyncio
import logging
from multipong.network.client import WSClient, StateBuffer


# Nastavení loggingu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DemoClient:
    """Demo konzolový klient pro testování."""
    
    def __init__(self, server_url: str = "ws://localhost:8000/ws", player_id: str = "auto"):
        self.server_url = server_url
        self.player_id = player_id
        self.buffer = StateBuffer()
        self.client: WSClient = None
        self.snapshot_count = 0
        self.running = True
    
    def on_snapshot(self, data: dict):
        """Callback pro příjem snapshot zpráv."""
        self.snapshot_count += 1
        self.buffer.add_state(data)
        
        # Logování každých 30 snapshotů
        if self.snapshot_count % 30 == 0:
            logger.info(f"📊 Přijato {self.snapshot_count} snapshotů")
            
            # Ukázka interpolace
            interpolated = self.buffer.get_interpolated()
            if interpolated and "ball" in interpolated:
                ball = interpolated["ball"]
                logger.info(f"   Míček: x={ball['x']:.1f}, y={ball['y']:.1f}")
    
    def on_connected(self, data: dict):
        """Callback pro connected zprávu."""
        assigned_slot = data.get("assigned_slot")
        lobby_status = data.get("lobby_status", {})
        
        logger.info(f"🎮 Připojeno!")
        logger.info(f"   Přidělená pozice: {assigned_slot}")
        logger.info(f"   Lobby: {lobby_status['players_count']}/{lobby_status['total_slots']} hráčů")
    
    def on_chat(self, sender: str, message: str):
        """Callback pro chat zprávy."""
        logger.info(f"💬 [{sender}]: {message}")
    
    async def run(self):
        """Spustí demo klienta."""
        logger.info("🚀 MULTIPONG Demo WebSocket Client")
        logger.info(f"   Server: {self.server_url}")
        logger.info(f"   Player ID: {self.player_id}")
        logger.info("")
        
        # Vytvoření klienta
        self.client = WSClient(
            url=self.server_url,
            player_id=self.player_id,
            on_snapshot=self.on_snapshot,
            on_connected=self.on_connected,
            on_chat=self.on_chat
        )
        
        # Připojení
        connected = await self.client.connect()
        if not connected:
            logger.error("❌ Nepodařilo se připojit k serveru")
            return
        
        logger.info("✅ Připojeno k serveru, čekám na zprávy...")
        logger.info("   (Pro ukončení stiskněte Ctrl+C)")
        logger.info("")
        
        try:
            # Simulace vstupu - každou sekundu posíláme input
            input_counter = 0
            ping_counter = 0
            
            while self.running and self.client.is_connected():
                await asyncio.sleep(1.0)
                
                # Každou sekundu posíláme vstup (střídavě nahoru/dolů)
                up = (input_counter % 2 == 0)
                down = not up
                await self.client.send_input(up=up, down=down)
                input_counter += 1
                
                # Každých 5 sekund ping
                ping_counter += 1
                if ping_counter >= 5:
                    await self.client.send_ping()
                    logger.info("💓 Ping odeslán")
                    ping_counter = 0
                
                # Každých 10 sekund zobrazíme status
                if input_counter % 10 == 0:
                    logger.info(f"📈 Status:")
                    logger.info(f"   Přijato snapshotů: {self.snapshot_count}")
                    logger.info(f"   Buffer: {self.buffer.size()} snapshotů")
                    logger.info(f"   Klient: {self.client}")
        
        except KeyboardInterrupt:
            logger.info("\n⚠️ Přerušeno uživatelem")
        
        finally:
            # Odpojení
            logger.info("Odpojuji se...")
            await self.client.disconnect()
            logger.info("🔌 Demo ukončeno")


async def main():
    """Hlavní funkce demo aplikace."""
    import sys
    
    # Parsování argumentů
    server_url = "ws://localhost:8000/ws"
    player_id = "auto"
    
    if len(sys.argv) > 1:
        player_id = sys.argv[1]
    
    if len(sys.argv) > 2:
        server_url = sys.argv[2]
    
    # Spuštění demo klienta
    demo = DemoClient(server_url=server_url, player_id=player_id)
    await demo.run()


if __name__ == "__main__":
    print("=" * 60)
    print("🏓 MULTIPONG Demo WebSocket Client")
    print("=" * 60)
    print()
    print("Použití:")
    print("  python -m multipong.network.client.demo_ws_client [player_id] [server_url]")
    print()
    print("Příklady:")
    print("  python -m multipong.network.client.demo_ws_client")
    print("  python -m multipong.network.client.demo_ws_client A1")
    print("  python -m multipong.network.client.demo_ws_client auto ws://localhost:8000/ws")
    print()
    print("=" * 60)
    print()
    
    asyncio.run(main())

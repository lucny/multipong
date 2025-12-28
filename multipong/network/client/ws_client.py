"""
WSClient - asynchronní WebSocket klient pro MULTIPONG Phase 5.
Připojení k serveru, posílání vstupů, příjem snapshotů.
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict
import websockets
from websockets.client import WebSocketClientProtocol


logger = logging.getLogger(__name__)


class WSClient:
    """
    Asynchronní klient pro komunikaci se serverem MULTIPONG.
    Odesílá vstupy a přijímá snapshoty.
    
    Attributes:
        url: URL WebSocket serveru (např. "ws://localhost:8000/ws")
        player_id: ID hráče (např. "A1", "auto")
        on_snapshot: Callback funkce volaná při příjmu snapshotu
        ws: WebSocket spojení
        running: Indikátor běhu listen smyčky
    """
    
    def __init__(
        self,
        url: str,
        player_id: str,
        on_snapshot: Optional[Callable[[dict], None]] = None,
        on_connected: Optional[Callable[[dict], None]] = None,
        on_chat: Optional[Callable[[str, str], None]] = None,
        on_pong: Optional[Callable[[dict], None]] = None
    ):
        """
        Inicializace WebSocket klienta.
        
        Args:
            url: URL serveru (např. "ws://localhost:8000/ws")
            player_id: ID hráče nebo "auto" pro automatické přidělení
            on_snapshot: Callback pro snapshot zprávy (dict) -> None
            on_connected: Callback pro connected zprávy (dict) -> None
            on_chat: Callback pro chat zprávy (player_id, message) -> None
            on_pong: Callback pro pong zprávy (dict) -> None
        """
        self.url = url
        self.player_id = player_id
        self.on_snapshot = on_snapshot
        self.on_connected = on_connected
        self.on_chat = on_chat
        self.on_pong = on_pong
        self.ws: Optional[WebSocketClientProtocol] = None
        self.running = False
        self.assigned_slot: Optional[str] = None
        self._listen_task: Optional[asyncio.Task] = None
    
    async def connect(self) -> bool:
        """
        Připojí se k WebSocket serveru.
        
        Returns:
            True pokud se připojení zdařilo, False jinak
        """
        try:
            full_url = f"{self.url}/{self.player_id}"
            logger.info(f"Připojuji se k {full_url}...")
            
            self.ws = await websockets.connect(full_url)
            self.running = True
            
            # Spuštění listen smyčky na pozadí
            self._listen_task = asyncio.create_task(self._listen())
            
            logger.info(f"✅ Připojeno k serveru jako {self.player_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Chyba při připojování: {e}")
            return False
    
    async def _listen(self) -> None:
        """
        Interní smyčka pro příjem zpráv od serveru.
        Běží na pozadí až do odpojení.
        """
        try:
            while self.running and self.ws:
                msg = await self.ws.recv()
                data = json.loads(msg)
                
                msg_type = data.get("type", "unknown")
                
                # Zpracování podle typu zprávy
                if msg_type == "snapshot":
                    if self.on_snapshot:
                        self.on_snapshot(data)
                
                elif msg_type == "connected":
                    # Server potvrdil připojení a přidělil slot
                    self.assigned_slot = data.get("assigned_slot")
                    logger.info(f"🎮 Přidělena pozice: {self.assigned_slot}")
                    if self.on_connected:
                        self.on_connected(data)
                
                elif msg_type == "chat":
                    # Chat zpráva od jiného hráče
                    sender = data.get("player_id", "unknown")
                    message = data.get("message", "")
                    logger.info(f"💬 [{sender}]: {message}")
                    if self.on_chat:
                        self.on_chat(sender, message)
                
                elif msg_type == "pong":
                    # Odpověď na ping
                    logger.debug("💓 Pong přijat")
                    if self.on_pong:
                        self.on_pong(data)
                
                elif msg_type == "error":
                    error_msg = data.get("message", "Unknown error")
                    logger.error(f"❌ Server error: {error_msg}")
                
                else:
                    logger.warning(f"⚠️ Neznámý typ zprávy: {msg_type}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔴 Spojení ukončeno serverem")
        
        except Exception as e:
            logger.error(f"❌ Chyba při příjmu zprávy: {e}", exc_info=True)
        
        finally:
            self.running = False
            logger.info("🔌 Listen smyčka ukončena")
    
    async def send_input(self, up: bool = False, down: bool = False) -> None:
        """
        Odesílá vstupy hráče serveru.
        
        Args:
            up: True pokud je stisknuta klávesa nahoru
            down: True pokud je stisknuta klávesa dolů
        """
        if self.ws and self.running:
            msg = {
                "type": "input",
                "up": up,
                "down": down
            }
            try:
                await self.ws.send(json.dumps(msg))
                logger.debug(f"⬆️{up} ⬇️{down}")
            except Exception as e:
                logger.error(f"❌ Chyba při odesílání inputu: {e}")
    
    async def send_chat(self, message: str) -> None:
        """
        Odešle chat zprávu všem hráčům.
        
        Args:
            message: Text zprávy
        """
        if self.ws and self.running:
            msg = {
                "type": "chat",
                "message": message
            }
            try:
                await self.ws.send(json.dumps(msg))
                logger.info(f"💬 Chat odeslán: {message}")
            except Exception as e:
                logger.error(f"❌ Chyba při odesílání chatu: {e}")
    
    async def send_ping(self, ping_id: Optional[str] = None) -> None:
        """
        Odešle ping zprávu pro keep-alive a latency měření.
        
        Args:
            ping_id: Volitelné ID pro tracování odpovědi (latency tracking)
        """
        if self.ws and self.running:
            msg = {"type": "ping"}
            if ping_id:
                msg["ping_id"] = ping_id
            try:
                await self.ws.send(json.dumps(msg))
                logger.debug("💓 Ping odeslán")
            except Exception as e:
                logger.error(f"❌ Chyba při odesílání pingu: {e}")
    
    async def disconnect(self) -> None:
        """Odpojí se od serveru."""
        logger.info("Odpojuji se od serveru...")
        self.running = False
        
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        logger.info("🔌 Odpojeno")
    
    def is_connected(self) -> bool:
        """
        Kontrola, zda je klient připojen.
        
        Returns:
            True pokud je aktivní spojení
        """
        return self.running and self.ws is not None
    
    def get_assigned_slot(self) -> Optional[str]:
        """
        Vrátí přidělenou pozici od serveru.
        
        Returns:
            Slot ID (např. "A1") nebo None pokud ještě nebyla přidělena
        """
        return self.assigned_slot
    
    def __repr__(self) -> str:
        """Textová reprezentace pro debugging."""
        status = "connected" if self.is_connected() else "disconnected"
        slot = self.assigned_slot or "not assigned"
        return f"WSClient(player_id={self.player_id}, slot={slot}, status={status})"

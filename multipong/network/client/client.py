"""
WebSocket klient pro připojení k MULTIPONG serveru
"""

import asyncio
import json
from typing import Optional, Callable
from websockets.asyncio.client import ClientConnection, connect


class MultiPongClient:
    """
    WebSocket klient pro MULTIPONG.
    """
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.websocket: Optional[ClientConnection] = None
        self.connected = False
        self.player_id: Optional[str] = None
    
    async def connect(self) -> bool:
        """Připojí se k serveru."""
        try:
            self.websocket = await connect(self.server_url)
            self.connected = True
            return True
        except Exception as e:
            print(f"Chyba při připojování: {e}")
            return False
    
    async def send_message(self, message_type: str, data: dict) -> None:
        """Odešle zprávu serveru."""
        if not self.websocket:
            return
        
        message = {
            "type": message_type,
            "data": data
        }
        await self.websocket.send(json.dumps(message))
    
    async def receive_message(self) -> Optional[dict]:
        """Přijme zprávu od serveru."""
        if not self.websocket:
            return None
        
        try:
            message = await self.websocket.recv()
            return json.loads(message)
        except Exception as e:
            print(f"Chyba při přijímání: {e}")
            return None
    
    async def disconnect(self) -> None:
        """Odpojí se od serveru."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False

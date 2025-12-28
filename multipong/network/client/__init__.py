"""
WebSocket klient pro MULTIPONG
Připojení k serveru, synchronizace stavu
"""

__version__ = "0.5.0"

from .ws_client import WSClient
from .state_buffer import StateBuffer

__all__ = [
	"WSClient",
	"StateBuffer",
]

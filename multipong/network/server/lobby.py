"""
Lobby management pro WebSocket server
"""

import asyncio
from typing import Dict, Set, Optional
from dataclasses import dataclass, field


@dataclass
class Player:
    """Reprezentace hráče v lobby."""
    player_id: str
    nickname: str
    slot: Optional[str] = None
    is_ready: bool = False


class Lobby:
    """
    Správa lobby pro MULTIPONG.
    Sloty: A1-A4 (tým A), B1-B4 (tým B)
    """
    
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.slots: Dict[str, Optional[str]] = {
            f"{team}{i}": None 
            for team in ['A', 'B'] 
            for i in range(1, 5)
        }
    
    async def add_player(self, player_id: str, nickname: str) -> bool:
        """Přidá hráče do lobby."""
        if player_id in self.players:
            return False
        
        self.players[player_id] = Player(
            player_id=player_id,
            nickname=nickname
        )
        return True
    
    async def assign_slot(self, player_id: str, slot: str) -> bool:
        """Přiřadí hráče do slotu."""
        if slot not in self.slots or self.slots[slot] is not None:
            return False
        
        if player_id not in self.players:
            return False
        
        self.slots[slot] = player_id
        self.players[player_id].slot = slot
        return True
    
    def get_lobby_state(self) -> dict:
        """Vrátí aktuální stav lobby."""
        return {
            "players": {
                pid: {
                    "nickname": p.nickname,
                    "slot": p.slot,
                    "ready": p.is_ready
                }
                for pid, p in self.players.items()
            },
            "slots": self.slots
        }

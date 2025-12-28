"""
Lobby management pro WebSocket server
"""

import asyncio
from typing import Dict, Set, Optional, List
from dataclasses import dataclass, field


@dataclass
class LobbySettings:
    """Configuration for a match."""
    match_duration: int = 180  # seconds
    goal_size: int = 200
    paddle_speed: float = 6.0
    ball_speed: float = 4.0
    max_score: Optional[int] = None  # None = time-based, else score-based


@dataclass
class Player:
    """Reprezentace hráče v lobby."""
    player_id: str
    nickname: str
    slot: Optional[str] = None
    is_ready: bool = False
    is_ai: bool = False
    ai_level: str = "simple"  # "simple", "predictive", "qlearning", "static"


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
        self.settings = LobbySettings()
    
    async def add_player(self, player_id: str, nickname: str, is_ai: bool = False) -> bool:
        """Přidá hráče do lobby."""
        if player_id in self.players:
            return False
        
        self.players[player_id] = Player(
            player_id=player_id,
            nickname=nickname,
            is_ai=is_ai,
            is_ready=is_ai  # AI is always ready
        )
        return True
    
    async def assign_slot(self, player_id: str, slot: str) -> bool:
        """Přiřadí hráče do slotu."""
        if slot not in self.slots or self.slots[slot] is not None:
            return False
        
        if player_id not in self.players:
            return False
        
        # Remove player from previous slot if they had one
        player = self.players[player_id]
        if player.slot:
            self.slots[player.slot] = None
        
        self.slots[slot] = player_id
        player.slot = slot
        return True
    
    async def free_slot(self, slot: str) -> bool:
        """Uvolní slot."""
        if slot not in self.slots:
            return False
        
        player_id = self.slots[slot]
        if player_id:
            self.slots[slot] = None
            if player_id in self.players:
                self.players[player_id].slot = None
            return True
        return False
    
    async def remove_player(self, player_id: str) -> bool:
        """Odstraní hráče z lobby."""
        if player_id not in self.players:
            return False
        
        player = self.players[player_id]
        if player.slot:
            self.slots[player.slot] = None
        
        del self.players[player_id]
        return True
    
    async def set_ready(self, player_id: str, is_ready: bool) -> bool:
        """Nastaví ready stav hráče."""
        if player_id not in self.players:
            return False
        
        self.players[player_id].is_ready = is_ready
        return True
    
    async def set_ai_level(self, slot: str, level: str) -> bool:
        """Nastaví úroveň AI pro slot."""
        if slot not in self.slots:
            return False
        
        player_id = self.slots[slot]
        if not player_id or player_id not in self.players:
            return False
        
        player = self.players[player_id]
        if not player.is_ai:
            return False
        
        player.ai_level = level
        return True
    
    def all_ready(self, min_players: int = 2) -> bool:
        """Zkontroluje, jestli jsou všichni přiřazení hráči ready."""
        occupied_slots = [p for p in self.players.values() if p.slot is not None]
        
        if len(occupied_slots) < min_players:
            return False
        
        return all(p.is_ready for p in occupied_slots)
    
    def get_occupied_slots(self) -> List[str]:
        """Vrátí seznam obsazených slotů."""
        return [slot for slot, pid in self.slots.items() if pid is not None]
    
    def get_team_slots(self, team: str) -> List[str]:
        """Vrátí obsazené sloty pro tým."""
        return [
            slot for slot in self.get_occupied_slots()
            if slot.startswith(team)
        ]
    
    def get_lobby_state(self) -> dict:
        """Vrátí aktuální stav lobby."""
        return {
            "slots": {
                slot: {
                    "player_id": pid,
                    "nickname": self.players[pid].nickname if pid else None,
                    "is_ai": self.players[pid].is_ai if pid else False,
                    "ai_level": self.players[pid].ai_level if (pid and self.players[pid].is_ai) else None,
                    "is_ready": self.players[pid].is_ready if pid else False,
                }
                for slot, pid in self.slots.items()
            },
            "ready_players": [
                p.nickname
                for p in self.players.values()
                if p.is_ready
            ],
            "settings": {
                "match_duration": self.settings.match_duration,
                "goal_size": self.settings.goal_size,
                "paddle_speed": self.settings.paddle_speed,
                "ball_speed": self.settings.ball_speed,
                "max_score": self.settings.max_score,
            }
        }
    
    def reset(self):
        """Reset lobby to initial state."""
        self.players.clear()
        for slot in self.slots:
            self.slots[slot] = None
        self.settings = LobbySettings()

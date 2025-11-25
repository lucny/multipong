"""
PlayerSession - reprezentace připojeného hráče.
Uchovává WebSocket spojení, ID hráče a aktuální vstup.
"""

import time
from typing import Dict
from fastapi import WebSocket


class PlayerSession:
    """
    Reprezentace jednoho připojeného hráče.
    
    Attributes:
        websocket: WebSocket spojení s klientem
        player_id: Unikátní ID hráče (např. "A1", "A2", "B1", "B2")
        current_input: Aktuální stav vstupů od hráče
        is_connected: Zda je hráč stále připojen
    """
    
    def __init__(self, websocket: WebSocket, player_id: str):
        """
        Inicializace herní relace hráče.
        
        Args:
            websocket: WebSocket spojení
            player_id: ID hráče
        """
        self.websocket: WebSocket = websocket
        self.player_id: str = player_id
        self.current_input: Dict[str, bool] = {
            "up": False,
            "down": False
        }
        self.is_connected: bool = True
        self.last_activity: float = time.time()
    
    def update_activity(self) -> None:
        """Aktualizuje čas poslední aktivity hráče."""
        self.last_activity = time.time()
    
    def get_idle_time(self) -> float:
        """
        Vrátí dobu nečinnosti v sekundách.
        
        Returns:
            Počet sekund od poslední aktivity
        """
        return time.time() - self.last_activity
    
    def update_input(self, up: bool = False, down: bool = False) -> None:
        """
        Aktualizuje aktuální stav vstupů od hráče.
        
        Args:
            up: Stav tlačítka nahoru
            down: Stav tlačítka dolů
        """
        self.current_input["up"] = up
        self.current_input["down"] = down
        self.update_activity()
    
    def get_input(self) -> Dict[str, bool]:
        """
        Vrátí aktuální stav vstupů.
        
        Returns:
            Slovník s klíči "up" a "down"
        """
        return self.current_input.copy()
    
    async def send_json(self, data: dict) -> None:
        """
        Odešle JSON zprávu klientovi.
        
        Args:
            data: Data k odeslání jako JSON
            
        Raises:
            Exception: Pokud odeslání selže
        """
        if self.is_connected:
            await self.websocket.send_json(data)
    
    def disconnect(self) -> None:
        """Označí session jako odpojenou."""
        self.is_connected = False
    
    def __repr__(self) -> str:
        """Textová reprezentace pro debugging."""
        status = "connected" if self.is_connected else "disconnected"
        return f"PlayerSession(id={self.player_id}, status={status}, input={self.current_input})"

"""
WebSocketManager - správa všech připojených hráčských relací.
"""

import logging
from typing import Dict, List, Optional
from .player_session import PlayerSession


logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Správce všech aktivních WebSocket připojení.
    
    Attributes:
        sessions: Slovník aktivních relací {player_id: PlayerSession}
    """
    
    def __init__(self):
        """Inicializace správce WebSocket spojení."""
        self.sessions: Dict[str, PlayerSession] = {}
    
    async def add(self, session: PlayerSession) -> bool:
        """
        Přidá novou relaci hráče.
        
        Args:
            session: PlayerSession k přidání
            
        Returns:
            True pokud byl hráč přidán, False pokud už existuje
        """
        if session.player_id in self.sessions:
            logger.warning(f"Hráč {session.player_id} je již připojen, odmítám duplicitní připojení")
            return False
        
        self.sessions[session.player_id] = session
        logger.info(f"✅ Přidán hráč {session.player_id} (celkem hráčů: {len(self.sessions)})")
        return True
    
    async def remove(self, session: PlayerSession) -> bool:
        """
        Odebere relaci hráče.
        
        Args:
            session: PlayerSession k odebrání
            
        Returns:
            True pokud byl hráč odebrán, False pokud nebyl nalezen
        """
        if session.player_id in self.sessions:
            del self.sessions[session.player_id]
            session.disconnect()
            logger.info(f"❌ Odebrán hráč {session.player_id} (zbývá hráčů: {len(self.sessions)})")
            return True
        
        logger.warning(f"Pokus o odebrání neexistujícího hráče {session.player_id}")
        return False
    
    async def remove_by_id(self, player_id: str) -> bool:
        """
        Odebere relaci podle ID hráče.
        
        Args:
            player_id: ID hráče k odebrání
            
        Returns:
            True pokud byl hráč odebrán, False pokud nebyl nalezen
        """
        if player_id in self.sessions:
            session = self.sessions[player_id]
            return await self.remove(session)
        return False
    
    def get_session(self, player_id: str) -> Optional[PlayerSession]:
        """
        Vrátí relaci podle ID hráče.
        
        Args:
            player_id: ID hráče
            
        Returns:
            PlayerSession nebo None pokud hráč není připojen
        """
        return self.sessions.get(player_id)
    
    def get_all_sessions(self) -> List[PlayerSession]:
        """
        Vrátí seznam všech aktivních relací.
        
        Returns:
            Seznam PlayerSession objektů
        """
        return list(self.sessions.values())
    
    def get_player_ids(self) -> List[str]:
        """
        Vrátí seznam ID všech připojených hráčů.
        
        Returns:
            Seznam player_id
        """
        return list(self.sessions.keys())
    
    def get_player_count(self) -> int:
        """
        Vrátí počet připojených hráčů.
        
        Returns:
            Počet aktivních relací
        """
        return len(self.sessions)
    
    async def broadcast(self, message: dict, exclude: Optional[List[str]] = None) -> int:
        """
        Rozešle JSON zprávu všem připojeným hráčům.
        
        Args:
            message: Slovník k odeslání jako JSON
            exclude: Seznam player_id, kterým se zpráva neodešle (optional)
            
        Returns:
            Počet hráčů, kterým byla zpráva úspěšně odeslána
        """
        exclude_set = set(exclude) if exclude else set()
        sent_count = 0
        failed_sessions = []
        
        for player_id, session in list(self.sessions.items()):
            # Přeskoč vyloučené hráče
            if player_id in exclude_set:
                continue
            
            try:
                await session.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Chyba při odesílání zprávy hráči {player_id}: {e}")
                failed_sessions.append(session)
        
        # Odeber hráče, kterým se nepodařilo odeslat zprávu
        for session in failed_sessions:
            await self.remove(session)
        
        return sent_count
    
    async def broadcast_to_team(self, message: dict, team: str) -> int:
        """
        Rozešle zprávu všem hráčům v daném týmu.
        
        Args:
            message: Slovník k odeslání jako JSON
            team: Označení týmu ("A" nebo "B")
            
        Returns:
            Počet hráčů, kterým byla zpráva odeslána
        """
        sent_count = 0
        
        for player_id, session in list(self.sessions.items()):
            # Kontrola, zda hráč patří do týmu (player_id začíná písmenem týmu)
            if player_id.startswith(team):
                try:
                    await session.send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Chyba při odesílání zprávy hráči {player_id}: {e}")
                    await self.remove(session)
        
        return sent_count
    
    def collect_inputs(self) -> Dict[str, Dict[str, bool]]:
        """
        Sesbírá aktuální vstupy od všech připojených hráčů.
        
        Returns:
            Slovník {player_id: {"up": bool, "down": bool}}
        """
        inputs = {}
        for player_id, session in self.sessions.items():
            inputs[player_id] = session.get_input()
        return inputs
    
    async def disconnect_inactive(self, timeout_seconds: float = 10.0) -> int:
        """
        Odpojí hráče, kteří neposlali žádnou zprávu po určitou dobu.
        
        Args:
            timeout_seconds: Maximální doba nečinnosti v sekundách (default 10s)
            
        Returns:
            Počet odpojených hráčů
        """
        disconnected_count = 0
        to_remove = []
        
        for player_id, session in self.sessions.items():
            idle_time = session.get_idle_time()
            if idle_time > timeout_seconds:
                logger.warning(f"⏱️ Hráč {player_id} neaktivní {idle_time:.1f}s, odpojuji")
                to_remove.append(session)
        
        for session in to_remove:
            await self.remove(session)
            disconnected_count += 1
        
        return disconnected_count
    
    async def disconnect_all(self) -> None:
        """Odpojí všechny hráče a vyčistí seznam relací."""
        logger.info(f"Odpojuji všechny hráče (celkem: {len(self.sessions)})")
        
        for session in list(self.sessions.values()):
            session.disconnect()
        
        self.sessions.clear()
        logger.info("Všichni hráči odpojeni")
    
    def __repr__(self) -> str:
        """Textová reprezentace pro debugging."""
        player_list = ", ".join(self.sessions.keys()) if self.sessions else "žádní"
        return f"WebSocketManager(players={len(self.sessions)}: {player_list})"

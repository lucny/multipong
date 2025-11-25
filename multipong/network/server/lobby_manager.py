"""
LobbyManager - automatické přidělování volných pálek hráčům.
"""

import logging
from typing import Dict, List, Optional, Set
from multipong.settings import PADDLE_HEIGHTS


logger = logging.getLogger(__name__)


class LobbyManager:
    """
    Správa lobby systému - přidělování volných pozic hráčům.
    
    Attributes:
        available_slots: Množina volných pozic (např. "A1", "B2")
        occupied_slots: Slovník obsazených pozic {player_id: slot}
    """
    
    def __init__(self):
        """Inicializace lobby manageru - načte volné pozice z konfigurace."""
        self.available_slots: Set[str] = set()
        self.occupied_slots: Dict[str, str] = {}
        
        # Načti volné pozice z konfigurace
        # Pokud má pozice výšku > 0, je aktivní a může být přidělena
        for slot, height in PADDLE_HEIGHTS.items():
            if height > 0:
                self.available_slots.add(slot)
        
        logger.info(f"🎮 Lobby inicializováno s {len(self.available_slots)} volnými pozicemi: {sorted(self.available_slots)}")
    
    def assign_slot(self, player_id: Optional[str] = None) -> Optional[str]:
        """
        Přidělí volnou pozici hráči.
        
        Args:
            player_id: Specifické ID pozice (např. "A1"), pokud None, přidělí první volnou
            
        Returns:
            Přidělené slot ID nebo None pokud není dostupné
        """
        # Pokud hráč má již přidělenou pozici, vrátíme ji
        if player_id and player_id in self.occupied_slots:
            logger.warning(f"Hráč {player_id} již má přidělenou pozici: {self.occupied_slots[player_id]}")
            return self.occupied_slots[player_id]
        
        # Pokud je specifikováno player_id a je volné
        if player_id and player_id in self.available_slots:
            self.available_slots.remove(player_id)
            self.occupied_slots[player_id] = player_id
            logger.info(f"✅ Přidělena požadovaná pozice: {player_id}")
            return player_id
        
        # Pokud je specifikováno player_id, ale není volné
        if player_id and player_id not in self.available_slots:
            # Zkusíme najít jinou volnou pozici
            if self.available_slots:
                slot = sorted(self.available_slots)[0]
                self.available_slots.remove(slot)
                self.occupied_slots[player_id] = slot
                logger.warning(f"⚠️ Pozice {player_id} není volná, přidělena {slot}")
                return slot
            else:
                logger.error(f"❌ Žádná volná pozice pro hráče {player_id}")
                return None
        
        # Automatické přidělení první volné pozice
        if self.available_slots:
            slot = sorted(self.available_slots)[0]
            # Generujeme dočasné player_id pokud nebylo zadáno
            temp_player_id = player_id if player_id else f"player_{slot}"
            self.available_slots.remove(slot)
            self.occupied_slots[temp_player_id] = slot
            logger.info(f"🎲 Automaticky přidělena pozice {slot} pro {temp_player_id}")
            return slot
        
        logger.error("❌ Žádné volné pozice v lobby")
        return None
    
    def release_slot(self, player_id: str) -> bool:
        """
        Uvolní pozici hráče zpět do lobby.
        
        Args:
            player_id: ID hráče
            
        Returns:
            True pokud byla pozice uvolněna, False pokud hráč nebyl nalezen
        """
        if player_id in self.occupied_slots:
            slot = self.occupied_slots[player_id]
            del self.occupied_slots[player_id]
            self.available_slots.add(slot)
            logger.info(f"🔓 Uvolněna pozice {slot} od hráče {player_id}")
            return True
        
        logger.warning(f"⚠️ Pokus o uvolnění neexistující pozice pro hráče {player_id}")
        return False
    
    def get_assigned_slot(self, player_id: str) -> Optional[str]:
        """
        Vrátí přidělenou pozici hráče.
        
        Args:
            player_id: ID hráče
            
        Returns:
            Slot ID nebo None pokud hráč nemá přidělenou pozici
        """
        return self.occupied_slots.get(player_id)
    
    def is_slot_available(self, slot: str) -> bool:
        """
        Kontroluje, zda je pozice volná.
        
        Args:
            slot: ID pozice (např. "A1")
            
        Returns:
            True pokud je pozice volná
        """
        return slot in self.available_slots
    
    def get_available_slots(self) -> List[str]:
        """
        Vrátí seznam volných pozic.
        
        Returns:
            Seřazený seznam volných slot ID
        """
        return sorted(self.available_slots)
    
    def get_occupied_slots(self) -> Dict[str, str]:
        """
        Vrátí slovník obsazených pozic.
        
        Returns:
            Slovník {player_id: slot}
        """
        return self.occupied_slots.copy()
    
    def get_player_count(self) -> int:
        """
        Vrátí počet přihlášených hráčů.
        
        Returns:
            Počet obsazených pozic
        """
        return len(self.occupied_slots)
    
    def get_lobby_status(self) -> dict:
        """
        Vrátí aktuální stav lobby.
        
        Returns:
            Slovník se statusem lobby
        """
        return {
            "available": sorted(self.available_slots),
            "occupied": self.occupied_slots.copy(),
            "total_slots": len(self.available_slots) + len(self.occupied_slots),
            "players_count": len(self.occupied_slots)
        }
    
    def reset(self) -> None:
        """Resetuje lobby do výchozího stavu - všechny pozice volné."""
        # Přesuneme všechny obsazené pozice zpět do volných
        for slot in self.occupied_slots.values():
            self.available_slots.add(slot)
        
        self.occupied_slots.clear()
        logger.info(f"🔄 Lobby resetováno, volných pozic: {len(self.available_slots)}")
    
    def __repr__(self) -> str:
        """Textová reprezentace pro debugging."""
        return f"LobbyManager(available={len(self.available_slots)}, occupied={len(self.occupied_slots)})"

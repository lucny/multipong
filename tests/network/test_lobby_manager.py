"""
Testy pro LobbyManager - automatické přidělování pozic hráčům.
"""

import pytest
from multipong.network.server.lobby_manager import LobbyManager


class TestLobbyManager:
    """Testy pro LobbyManager."""
    
    def test_lobby_initialization(self):
        """Test inicializace lobby s volnými pozicemi z konfigurace."""
        lobby = LobbyManager()
        
        # Mělo by být načteno 6 aktivních pozic (A2=0, B3=0 jsou neaktivní)
        status = lobby.get_lobby_status()
        assert status["total_slots"] == 6
        assert status["players_count"] == 0
        assert len(status["available"]) == 6
        assert "A1" in status["available"]
        assert "B1" in status["available"]
        # A2 a B3 by neměly být dostupné (height=0)
        assert "A2" not in status["available"]
        assert "B3" not in status["available"]
    
    def test_assign_specific_slot(self):
        """Test přidělení konkrétní pozice."""
        lobby = LobbyManager()
        
        slot = lobby.assign_slot("A1")
        assert slot == "A1"
        assert not lobby.is_slot_available("A1")
        assert lobby.get_assigned_slot("A1") == "A1"
    
    def test_assign_auto_slot(self):
        """Test automatického přidělení volné pozice."""
        lobby = LobbyManager()
        
        slot = lobby.assign_slot()
        assert slot is not None
        assert slot in ["A1", "A3", "A4", "B1", "B2", "B4"]
        assert not lobby.is_slot_available(slot)
    
    def test_assign_occupied_slot_returns_alternative(self):
        """Test přidělení alternativní pozice, pokud požadovaná je obsazená."""
        lobby = LobbyManager()
        
        # Obsadíme A1
        lobby.assign_slot("A1")
        
        # Pokusíme se přidělit A1 jinému hráči
        slot = lobby.assign_slot("player2")
        assert slot is not None
        assert slot != "A1"  # Měla by být přidělena jiná pozice
    
    def test_release_slot(self):
        """Test uvolnění pozice."""
        lobby = LobbyManager()
        
        # Přidělíme pozici
        lobby.assign_slot("A1")
        assert not lobby.is_slot_available("A1")
        
        # Uvolníme ji
        result = lobby.release_slot("A1")
        assert result is True
        assert lobby.is_slot_available("A1")
        assert lobby.get_assigned_slot("A1") is None
    
    def test_release_nonexistent_slot(self):
        """Test pokusu o uvolnění neexistující pozice."""
        lobby = LobbyManager()
        
        result = lobby.release_slot("nonexistent")
        assert result is False
    
    def test_get_available_slots(self):
        """Test získání seznamu volných pozic."""
        lobby = LobbyManager()
        
        # Na začátku by měly být všechny aktivní pozice volné
        available = lobby.get_available_slots()
        assert len(available) == 6
        assert sorted(available) == available  # Mělo by být seřazené
        
        # Obsadíme jednu pozici
        lobby.assign_slot("A1")
        available = lobby.get_available_slots()
        assert len(available) == 5
        assert "A1" not in available
    
    def test_get_occupied_slots(self):
        """Test získání slovníku obsazených pozic."""
        lobby = LobbyManager()
        
        lobby.assign_slot("A1")
        lobby.assign_slot("B1")
        
        occupied = lobby.get_occupied_slots()
        assert len(occupied) == 2
        assert occupied["A1"] == "A1"
        assert occupied["B1"] == "B1"
    
    def test_lobby_status(self):
        """Test získání komplexního statusu lobby."""
        lobby = LobbyManager()
        
        lobby.assign_slot("A1")
        
        status = lobby.get_lobby_status()
        assert status["total_slots"] == 6
        assert status["players_count"] == 1
        assert len(status["available"]) == 5
        assert "A1" in status["occupied"]
    
    def test_reset_lobby(self):
        """Test resetování lobby."""
        lobby = LobbyManager()
        
        # Obsadíme několik pozic
        lobby.assign_slot("A1")
        lobby.assign_slot("B1")
        lobby.assign_slot("A3")
        
        assert lobby.get_player_count() == 3
        
        # Resetujeme
        lobby.reset()
        
        status = lobby.get_lobby_status()
        assert status["players_count"] == 0
        assert len(status["available"]) == 6
        assert len(status["occupied"]) == 0
    
    def test_full_lobby(self):
        """Test chování při plném lobby."""
        lobby = LobbyManager()
        
        # Obsadíme všechny pozice
        slots = lobby.get_available_slots()
        for slot in slots:
            lobby.assign_slot(slot)
        
        # Pokus o přidělení další pozice
        slot = lobby.assign_slot()
        assert slot is None
        
        status = lobby.get_lobby_status()
        assert status["players_count"] == 6
        assert len(status["available"]) == 0
    
    def test_assign_inactive_slot(self):
        """Test pokusu o přidělení neaktivní pozice (height=0)."""
        lobby = LobbyManager()
        
        # A2 a B3 mají height=0, neměly by být dostupné
        slot = lobby.assign_slot("A2")
        # Měla by být přidělena alternativní pozice, ne A2
        assert slot is not None
        assert slot != "A2"
        assert lobby.is_slot_available("A2") is False  # A2 nikdy nebylo volné
    
    def test_is_slot_available(self):
        """Test kontroly dostupnosti pozice."""
        lobby = LobbyManager()
        
        assert lobby.is_slot_available("A1") is True
        
        lobby.assign_slot("A1")
        assert lobby.is_slot_available("A1") is False
        
        lobby.release_slot("A1")
        assert lobby.is_slot_available("A1") is True
    
    def test_get_assigned_slot(self):
        """Test získání přidělené pozice hráče."""
        lobby = LobbyManager()
        
        lobby.assign_slot("A1")
        assert lobby.get_assigned_slot("A1") == "A1"
        assert lobby.get_assigned_slot("nonexistent") is None
    
    def test_get_player_count(self):
        """Test získání počtu hráčů v lobby - přidáno pro WebSocketManager."""
        lobby = LobbyManager()
        
        # Poznámka: get_player_count není přímo v LobbyManager,
        # ale v lobby_status můžeme získat players_count
        status = lobby.get_lobby_status()
        assert status["players_count"] == 0
        
        lobby.assign_slot("A1")
        status = lobby.get_lobby_status()
        assert status["players_count"] == 1

"""
Unit testy pro PlayerSession a WebSocketManager.
"""

import time
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from multipong.network.server.player_session import PlayerSession
from multipong.network.server.websocket_manager import WebSocketManager


class TestPlayerSession:
    """Testy pro třídu PlayerSession."""
    
    def test_init(self):
        """Test inicializace PlayerSession."""
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        assert session.player_id == "A1"
        assert session.websocket is mock_ws
        assert session.current_input == {"up": False, "down": False}
        assert session.is_connected is True
    
    def test_update_input(self):
        """Test aktualizace vstupů."""
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        # Default
        assert session.current_input == {"up": False, "down": False}
        
        # Update UP
        session.update_input(up=True, down=False)
        assert session.current_input == {"up": True, "down": False}
        
        # Update DOWN
        session.update_input(up=False, down=True)
        assert session.current_input == {"up": False, "down": True}
        
        # Update both
        session.update_input(up=True, down=True)
        assert session.current_input == {"up": True, "down": True}
    
    def test_get_input(self):
        """Test získání kopie vstupů."""
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        session.update_input(up=True, down=False)
        
        inputs = session.get_input()
        assert inputs == {"up": True, "down": False}
        
        # Změna kopie by neměla ovlivnit originál
        inputs["up"] = False
        assert session.current_input["up"] is True
    
    @pytest.mark.asyncio
    async def test_send_json(self):
        """Test odeslání JSON zprávy."""
        mock_ws = AsyncMock()
        session = PlayerSession(mock_ws, "A1")
        
        data = {"type": "test", "value": 123}
        await session.send_json(data)
        
        mock_ws.send_json.assert_called_once_with(data)
    
    @pytest.mark.asyncio
    async def test_send_json_when_disconnected(self):
        """Test že odpojená session neposílá zprávy."""
        mock_ws = AsyncMock()
        session = PlayerSession(mock_ws, "A1")
        session.disconnect()
        
        data = {"type": "test"}
        await session.send_json(data)
        
        # Nemělo by být voláno
        mock_ws.send_json.assert_not_called()
    
    def test_disconnect(self):
        """Test odpojení session."""
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        assert session.is_connected is True
        session.disconnect()
        assert session.is_connected is False
    
    def test_repr(self):
        """Test textové reprezentace."""
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        repr_str = repr(session)
        assert "A1" in repr_str
        assert "connected" in repr_str


class TestWebSocketManager:
    """Testy pro třídu WebSocketManager."""
    
    @pytest.mark.asyncio
    async def test_init(self):
        """Test inicializace WebSocketManager."""
        manager = WebSocketManager()
        assert manager.sessions == {}
        assert manager.get_player_count() == 0
    
    @pytest.mark.asyncio
    async def test_add_session(self):
        """Test přidání nové session."""
        manager = WebSocketManager()
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        result = await manager.add(session)
        assert result is True
        assert manager.get_player_count() == 1
        assert "A1" in manager.sessions
    
    @pytest.mark.asyncio
    async def test_add_duplicate_session(self):
        """Test odmítnutí duplicitního přidání."""
        manager = WebSocketManager()
        mock_ws1 = Mock()
        mock_ws2 = Mock()
        
        session1 = PlayerSession(mock_ws1, "A1")
        session2 = PlayerSession(mock_ws2, "A1")
        
        result1 = await manager.add(session1)
        result2 = await manager.add(session2)
        
        assert result1 is True
        assert result2 is False
        assert manager.get_player_count() == 1
    
    @pytest.mark.asyncio
    async def test_remove_session(self):
        """Test odebrání session."""
        manager = WebSocketManager()
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        await manager.add(session)
        assert manager.get_player_count() == 1
        
        result = await manager.remove(session)
        assert result is True
        assert manager.get_player_count() == 0
        assert session.is_connected is False
    
    @pytest.mark.asyncio
    async def test_remove_nonexistent_session(self):
        """Test odebrání neexistující session."""
        manager = WebSocketManager()
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        result = await manager.remove(session)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_remove_by_id(self):
        """Test odebrání session podle ID."""
        manager = WebSocketManager()
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        await manager.add(session)
        result = await manager.remove_by_id("A1")
        
        assert result is True
        assert manager.get_player_count() == 0
    
    @pytest.mark.asyncio
    async def test_get_session(self):
        """Test získání session podle ID."""
        manager = WebSocketManager()
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        await manager.add(session)
        
        retrieved = manager.get_session("A1")
        assert retrieved is session
        
        none_session = manager.get_session("B1")
        assert none_session is None
    
    @pytest.mark.asyncio
    async def test_get_all_sessions(self):
        """Test získání všech sessions."""
        manager = WebSocketManager()
        
        session1 = PlayerSession(Mock(), "A1")
        session2 = PlayerSession(Mock(), "B1")
        
        await manager.add(session1)
        await manager.add(session2)
        
        sessions = manager.get_all_sessions()
        assert len(sessions) == 2
        assert session1 in sessions
        assert session2 in sessions
    
    @pytest.mark.asyncio
    async def test_get_player_ids(self):
        """Test získání seznamu player IDs."""
        manager = WebSocketManager()
        
        await manager.add(PlayerSession(Mock(), "A1"))
        await manager.add(PlayerSession(Mock(), "A2"))
        await manager.add(PlayerSession(Mock(), "B1"))
        
        player_ids = manager.get_player_ids()
        assert len(player_ids) == 3
        assert "A1" in player_ids
        assert "A2" in player_ids
        assert "B1" in player_ids
    
    @pytest.mark.asyncio
    async def test_broadcast(self):
        """Test broadcastu zprávy všem hráčům."""
        manager = WebSocketManager()
        
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        
        session1 = PlayerSession(mock_ws1, "A1")
        session2 = PlayerSession(mock_ws2, "B1")
        
        await manager.add(session1)
        await manager.add(session2)
        
        message = {"type": "snapshot", "data": "test"}
        sent_count = await manager.broadcast(message)
        
        assert sent_count == 2
        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_broadcast_with_exclude(self):
        """Test broadcastu s vyloučením hráčů."""
        manager = WebSocketManager()
        
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        
        session1 = PlayerSession(mock_ws1, "A1")
        session2 = PlayerSession(mock_ws2, "B1")
        
        await manager.add(session1)
        await manager.add(session2)
        
        message = {"type": "snapshot"}
        sent_count = await manager.broadcast(message, exclude=["A1"])
        
        assert sent_count == 1
        mock_ws1.send_json.assert_not_called()
        mock_ws2.send_json.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_broadcast_to_team(self):
        """Test broadcastu pouze jednomu týmu."""
        manager = WebSocketManager()
        
        mock_ws_a1 = AsyncMock()
        mock_ws_a2 = AsyncMock()
        mock_ws_b1 = AsyncMock()
        
        await manager.add(PlayerSession(mock_ws_a1, "A1"))
        await manager.add(PlayerSession(mock_ws_a2, "A2"))
        await manager.add(PlayerSession(mock_ws_b1, "B1"))
        
        message = {"type": "team_message"}
        sent_count = await manager.broadcast_to_team(message, "A")
        
        assert sent_count == 2
        mock_ws_a1.send_json.assert_called_once_with(message)
        mock_ws_a2.send_json.assert_called_once_with(message)
        mock_ws_b1.send_json.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_collect_inputs(self):
        """Test sesbírání vstupů od všech hráčů."""
        manager = WebSocketManager()
        
        session1 = PlayerSession(Mock(), "A1")
        session2 = PlayerSession(Mock(), "B1")
        
        session1.update_input(up=True, down=False)
        session2.update_input(up=False, down=True)
        
        await manager.add(session1)
        await manager.add(session2)
        
        inputs = manager.collect_inputs()
        
        assert inputs == {
            "A1": {"up": True, "down": False},
            "B1": {"up": False, "down": True}
        }
    
    @pytest.mark.asyncio
    async def test_disconnect_all(self):
        """Test odpojení všech hráčů."""
        manager = WebSocketManager()
        
        session1 = PlayerSession(Mock(), "A1")
        session2 = PlayerSession(Mock(), "B1")
        
        await manager.add(session1)
        await manager.add(session2)
        
        assert manager.get_player_count() == 2
        
        await manager.disconnect_all()
        
        assert manager.get_player_count() == 0
        assert session1.is_connected is False
        assert session2.is_connected is False
    
    @pytest.mark.asyncio
    async def test_repr(self):
        """Test textové reprezentace."""
        manager = WebSocketManager()
        await manager.add(PlayerSession(Mock(), "A1"))
        await manager.add(PlayerSession(Mock(), "B1"))
        
        repr_str = repr(manager)
        assert "2" in repr_str or "A1" in repr_str


class TestPlayerSessionTimeout:
    """Testy pro timeout funkcionalitu v PlayerSession."""
    
    def test_last_activity_initialization(self):
        """Test inicializace last_activity timestampu."""
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        assert hasattr(session, "last_activity")
        assert isinstance(session.last_activity, float)
        assert session.last_activity <= time.time()
    
    def test_update_activity(self):
        """Test aktualizace času poslední aktivity."""
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        initial_time = session.last_activity
        time.sleep(0.1)
        
        session.update_activity()
        assert session.last_activity > initial_time
    
    def test_get_idle_time(self):
        """Test získání doby nečinnosti."""
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        # Bezprostředně po vytvoření by měl být idle time ~0
        idle = session.get_idle_time()
        assert idle >= 0
        assert idle < 0.1  # Méně než 100ms
        
        # Po čekání by měl narůst
        time.sleep(0.2)
        idle = session.get_idle_time()
        assert idle >= 0.2
    
    def test_update_input_updates_activity(self):
        """Test, že update_input aktualizuje také aktivitu."""
        mock_ws = Mock()
        session = PlayerSession(mock_ws, "A1")
        
        time.sleep(0.1)
        initial_time = session.last_activity
        
        session.update_input(up=True)
        assert session.last_activity > initial_time


class TestWebSocketManagerTimeout:
    """Testy pro timeout funkcionalitu v WebSocketManager."""
    
    @pytest.mark.asyncio
    async def test_disconnect_inactive_no_timeout(self):
        """Test, že aktivní hráči nejsou odpojeni."""
        manager = WebSocketManager()
        mock_ws = Mock()
        mock_ws.send_json = AsyncMock()
        
        session = PlayerSession(mock_ws, "A1")
        await manager.add(session)
        
        # Bezprostředně by neměl být nikdo odpojen
        disconnected = await manager.disconnect_inactive(timeout_seconds=10.0)
        assert disconnected == 0
        assert manager.get_player_count() == 1
    
    @pytest.mark.asyncio
    async def test_disconnect_inactive_with_timeout(self):
        """Test, že neaktivní hráči jsou odpojeni."""
        manager = WebSocketManager()
        mock_ws = Mock()
        mock_ws.send_json = AsyncMock()
        
        session = PlayerSession(mock_ws, "A1")
        await manager.add(session)
        
        # Simulujeme starou aktivitu (11 sekund zpět)
        session.last_activity = time.time() - 11.0
        
        # Odpojení s timeoutem 10s
        disconnected = await manager.disconnect_inactive(timeout_seconds=10.0)
        assert disconnected == 1
        assert manager.get_player_count() == 0
    
    @pytest.mark.asyncio
    async def test_disconnect_inactive_multiple_players(self):
        """Test odpojení pouze neaktivních hráčů z více připojených."""
        manager = WebSocketManager()
        
        # Vytvoříme 3 hráče
        session1 = PlayerSession(Mock(), "A1")
        session2 = PlayerSession(Mock(), "A2")
        session3 = PlayerSession(Mock(), "B1")
        
        await manager.add(session1)
        await manager.add(session2)
        await manager.add(session3)
        
        # Nastavíme neaktivitu pro session1 a session3
        session1.last_activity = time.time() - 11.0
        session3.last_activity = time.time() - 12.0
        # session2 zůstane aktivní
        
        disconnected = await manager.disconnect_inactive(timeout_seconds=10.0)
        assert disconnected == 2
        assert manager.get_player_count() == 1
        assert manager.get_session("A2") is not None
        assert manager.get_session("A1") is None
        assert manager.get_session("B1") is None
    
    @pytest.mark.asyncio
    async def test_disconnect_inactive_custom_timeout(self):
        """Test s vlastním timeout limitem."""
        manager = WebSocketManager()
        session = PlayerSession(Mock(), "A1")
        await manager.add(session)
        
        # Simulujeme aktivitu před 3 sekundami
        session.last_activity = time.time() - 3.0
        
        # S timeoutem 5s by neměl být odpojen
        disconnected = await manager.disconnect_inactive(timeout_seconds=5.0)
        assert disconnected == 0
        
        # S timeoutem 2s by měl být odpojen
        disconnected = await manager.disconnect_inactive(timeout_seconds=2.0)
        assert disconnected == 1


"""
Unit testy pro WSClient a StateBuffer.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from multipong.network.client.ws_client import WSClient
from multipong.network.client.state_buffer import StateBuffer


class TestWSClient:
    """Testy pro WSClient."""
    
    def test_init(self):
        """Test inicializace WSClient."""
        on_snapshot = Mock()
        client = WSClient("ws://localhost:8000/ws", "A1", on_snapshot)
        
        assert client.url == "ws://localhost:8000/ws"
        assert client.player_id == "A1"
        assert client.on_snapshot is on_snapshot
        assert client.ws is None
        assert client.running is False
        assert client.assigned_slot is None
    
    def test_init_with_callbacks(self):
        """Test inicializace s callback funkcemi."""
        on_snapshot = Mock()
        on_connected = Mock()
        on_chat = Mock()
        
        client = WSClient(
            "ws://localhost:8000/ws",
            "A1",
            on_snapshot=on_snapshot,
            on_connected=on_connected,
            on_chat=on_chat
        )
        
        assert client.on_snapshot is on_snapshot
        assert client.on_connected is on_connected
        assert client.on_chat is on_chat
    
    def test_is_connected_initially_false(self):
        """Test, že is_connected je zpočátku False."""
        client = WSClient("ws://localhost:8000/ws", "A1")
        assert client.is_connected() is False
    
    def test_get_assigned_slot_initially_none(self):
        """Test, že assigned_slot je zpočátku None."""
        client = WSClient("ws://localhost:8000/ws", "A1")
        assert client.get_assigned_slot() is None
    
    def test_repr(self):
        """Test textové reprezentace."""
        client = WSClient("ws://localhost:8000/ws", "A1")
        repr_str = repr(client)
        assert "A1" in repr_str
        assert "disconnected" in repr_str


class TestStateBuffer:
    """Testy pro StateBuffer."""
    
    def test_init(self):
        """Test inicializace StateBuffer."""
        buffer = StateBuffer()
        assert buffer.size() == 0
        assert buffer.max_size == 3
    
    def test_init_with_custom_size(self):
        """Test inicializace s vlastní velikostí."""
        buffer = StateBuffer(max_size=5)
        assert buffer.max_size == 5
    
    def test_add_state(self):
        """Test přidání stavu."""
        buffer = StateBuffer()
        state = {"ball": {"x": 100, "y": 200}}
        
        buffer.add_state(state)
        assert buffer.size() == 1
    
    def test_add_multiple_states(self):
        """Test přidání více stavů."""
        buffer = StateBuffer()
        
        for i in range(5):
            buffer.add_state({"ball": {"x": i * 10, "y": i * 20}})
        
        # Buffer má max_size=3, měly by zůstat jen poslední 3
        assert buffer.size() == 3
    
    def test_get_latest(self):
        """Test získání posledního stavu."""
        buffer = StateBuffer()
        
        state1 = {"ball": {"x": 100, "y": 200}}
        state2 = {"ball": {"x": 150, "y": 250}}
        
        buffer.add_state(state1)
        buffer.add_state(state2)
        
        latest = buffer.get_latest()
        assert latest["ball"]["x"] == 150
        assert latest["ball"]["y"] == 250
    
    def test_get_latest_empty_buffer(self):
        """Test get_latest na prázdném bufferu."""
        buffer = StateBuffer()
        assert buffer.get_latest() is None
    
    def test_get_interpolated_single_state(self):
        """Test interpolace s jediným stavem."""
        buffer = StateBuffer()
        state = {"ball": {"x": 100, "y": 200}}
        buffer.add_state(state)
        
        # S jediným stavem by měl vrátit ten samý
        interpolated = buffer.get_interpolated()
        assert interpolated["ball"]["x"] == 100
        assert interpolated["ball"]["y"] == 200
    
    def test_get_interpolated_two_states(self):
        """Test interpolace mezi dvěma stavy."""
        buffer = StateBuffer()
        
        state1 = {
            "ball": {"x": 100.0, "y": 200.0, "radius": 10},
            "team_left": {"name": "Left", "score": 0, "paddles": []},
            "team_right": {"name": "Right", "score": 0, "paddles": []},
            "goal_left": {"top": 0, "bottom": 100},
            "goal_right": {"top": 0, "bottom": 100}
        }
        
        time.sleep(0.05)  # Krátká pauza mezi snapshoty
        
        state2 = {
            "ball": {"x": 200.0, "y": 300.0, "radius": 10},
            "team_left": {"name": "Left", "score": 0, "paddles": []},
            "team_right": {"name": "Right", "score": 0, "paddles": []},
            "goal_left": {"top": 0, "bottom": 100},
            "goal_right": {"top": 0, "bottom": 100}
        }
        
        buffer.add_state(state1)
        buffer.add_state(state2)
        
        # Interpolovaná hodnota by měla být mezi 100-200 pro x
        interpolated = buffer.get_interpolated()
        assert interpolated is not None
        assert 100 <= interpolated["ball"]["x"] <= 200
        assert 200 <= interpolated["ball"]["y"] <= 300
    
    def test_interpolate_ball(self):
        """Test interpolace míčku."""
        buffer = StateBuffer()
        
        ball1 = {"x": 0.0, "y": 0.0, "radius": 10}
        ball2 = {"x": 100.0, "y": 100.0, "radius": 10}
        
        # Alpha = 0.5 (střed)
        result = buffer._interpolate_ball(ball1, ball2, 0.5)
        assert result["x"] == 50.0
        assert result["y"] == 50.0
        assert result["radius"] == 10
        
        # Alpha = 0.0 (ball1)
        result = buffer._interpolate_ball(ball1, ball2, 0.0)
        assert result["x"] == 0.0
        assert result["y"] == 0.0
        
        # Alpha = 1.0 (ball2)
        result = buffer._interpolate_ball(ball1, ball2, 1.0)
        assert result["x"] == 100.0
        assert result["y"] == 100.0
    
    def test_interpolate_team(self):
        """Test interpolace týmu."""
        buffer = StateBuffer()
        
        team1 = {
            "name": "Left",
            "score": 2,
            "paddles": [
                {"player_id": "A1", "x": 10, "y": 100, "width": 10, "height": 50}
            ]
        }
        
        team2 = {
            "name": "Left",
            "score": 3,
            "paddles": [
                {"player_id": "A1", "x": 10, "y": 200, "width": 10, "height": 50}
            ]
        }
        
        # Alpha = 0.5
        result = buffer._interpolate_team(team1, team2, 0.5)
        assert result["score"] == 3  # Score se nekopíruje z nejnovějšího
        assert len(result["paddles"]) == 1
        assert result["paddles"][0]["y"] == 150  # (100 + 200) / 2
    
    def test_clear(self):
        """Test vyčištění bufferu."""
        buffer = StateBuffer()
        buffer.add_state({"ball": {"x": 100, "y": 200}})
        buffer.add_state({"ball": {"x": 150, "y": 250}})
        
        assert buffer.size() == 2
        
        buffer.clear()
        assert buffer.size() == 0
    
    def test_repr(self):
        """Test textové reprezentace."""
        buffer = StateBuffer()
        buffer.add_state({"ball": {"x": 100, "y": 200}})
        
        repr_str = repr(buffer)
        assert "1" in repr_str
        assert "3" in repr_str  # max_size


@pytest.mark.asyncio
class TestWSClientAsync:
    """Asynchronní testy pro WSClient."""
    
    async def test_send_input(self):
        """Test odeslání input zprávy."""
        client = WSClient("ws://localhost:8000/ws", "A1")
        
        # Mock WebSocket
        mock_ws = AsyncMock()
        client.ws = mock_ws
        client.running = True
        
        await client.send_input(up=True, down=False)
        
        # Ověření, že byla zavolána send
        mock_ws.send.assert_called_once()
        call_args = mock_ws.send.call_args[0][0]
        assert '"type": "input"' in call_args
        assert '"up": true' in call_args
        assert '"down": false' in call_args
    
    async def test_send_chat(self):
        """Test odeslání chat zprávy."""
        client = WSClient("ws://localhost:8000/ws", "A1")
        
        mock_ws = AsyncMock()
        client.ws = mock_ws
        client.running = True
        
        await client.send_chat("Hello!")
        
        mock_ws.send.assert_called_once()
        call_args = mock_ws.send.call_args[0][0]
        assert '"type": "chat"' in call_args
        assert '"message": "Hello!"' in call_args
    
    async def test_send_ping(self):
        """Test odeslání ping zprávy."""
        client = WSClient("ws://localhost:8000/ws", "A1")
        
        mock_ws = AsyncMock()
        client.ws = mock_ws
        client.running = True
        
        await client.send_ping()
        
        mock_ws.send.assert_called_once()
        call_args = mock_ws.send.call_args[0][0]
        assert '"type": "ping"' in call_args
    
    async def test_disconnect(self):
        """Test odpojení od serveru."""
        client = WSClient("ws://localhost:8000/ws", "A1")
        
        mock_ws = AsyncMock()
        client.ws = mock_ws
        client.running = True
        
        await client.disconnect()
        
        assert client.running is False
        mock_ws.close.assert_called_once()

"""
Tests for Lobby functionality.
"""

import pytest
import asyncio
from multipong.network.server.lobby import Lobby, Player, LobbySettings


@pytest.fixture
def lobby():
    """Create a fresh lobby instance."""
    return Lobby()


@pytest.mark.asyncio
async def test_lobby_initialization(lobby):
    """Test that lobby initializes with empty slots."""
    assert len(lobby.slots) == 8
    assert all(slot_id is None for slot_id in lobby.slots.values())
    assert len(lobby.players) == 0


@pytest.mark.asyncio
async def test_add_player(lobby):
    """Test adding a player to lobby."""
    result = await lobby.add_player("player1", "Alice")
    assert result is True
    assert "player1" in lobby.players
    assert lobby.players["player1"].nickname == "Alice"


@pytest.mark.asyncio
async def test_add_duplicate_player(lobby):
    """Test that adding duplicate player fails."""
    await lobby.add_player("player1", "Alice")
    result = await lobby.add_player("player1", "Bob")
    assert result is False
    assert lobby.players["player1"].nickname == "Alice"  # Original remains


@pytest.mark.asyncio
async def test_assign_slot(lobby):
    """Test assigning player to a slot."""
    await lobby.add_player("player1", "Alice")
    result = await lobby.assign_slot("player1", "A1")
    
    assert result is True
    assert lobby.slots["A1"] == "player1"
    assert lobby.players["player1"].slot == "A1"


@pytest.mark.asyncio
async def test_assign_occupied_slot(lobby):
    """Test that assigning to occupied slot fails."""
    await lobby.add_player("player1", "Alice")
    await lobby.add_player("player2", "Bob")
    
    await lobby.assign_slot("player1", "A1")
    result = await lobby.assign_slot("player2", "A1")
    
    assert result is False
    assert lobby.slots["A1"] == "player1"


@pytest.mark.asyncio
async def test_reassign_player_slot(lobby):
    """Test reassigning player to a different slot."""
    await lobby.add_player("player1", "Alice")
    await lobby.assign_slot("player1", "A1")
    await lobby.assign_slot("player1", "B2")
    
    assert lobby.slots["A1"] is None  # Old slot freed
    assert lobby.slots["B2"] == "player1"  # New slot assigned
    assert lobby.players["player1"].slot == "B2"


@pytest.mark.asyncio
async def test_free_slot(lobby):
    """Test freeing a slot."""
    await lobby.add_player("player1", "Alice")
    await lobby.assign_slot("player1", "A1")
    
    result = await lobby.free_slot("A1")
    assert result is True
    assert lobby.slots["A1"] is None
    assert lobby.players["player1"].slot is None


@pytest.mark.asyncio
async def test_remove_player(lobby):
    """Test removing a player from lobby."""
    await lobby.add_player("player1", "Alice")
    await lobby.assign_slot("player1", "A1")
    
    result = await lobby.remove_player("player1")
    assert result is True
    assert "player1" not in lobby.players
    assert lobby.slots["A1"] is None


@pytest.mark.asyncio
async def test_set_ready(lobby):
    """Test setting player ready state."""
    await lobby.add_player("player1", "Alice")
    await lobby.assign_slot("player1", "A1")
    
    result = await lobby.set_ready("player1", True)
    assert result is True
    assert lobby.players["player1"].is_ready is True


@pytest.mark.asyncio
async def test_all_ready_minimum_players(lobby):
    """Test all_ready with minimum player requirement."""
    await lobby.add_player("player1", "Alice")
    await lobby.assign_slot("player1", "A1")
    await lobby.set_ready("player1", True)
    
    # One player is not enough (min 2)
    assert lobby.all_ready(min_players=2) is False
    
    await lobby.add_player("player2", "Bob")
    await lobby.assign_slot("player2", "B1")
    await lobby.set_ready("player2", True)
    
    # Two players, both ready
    assert lobby.all_ready(min_players=2) is True


@pytest.mark.asyncio
async def test_all_ready_not_all_ready(lobby):
    """Test all_ready when not all players are ready."""
    await lobby.add_player("player1", "Alice")
    await lobby.add_player("player2", "Bob")
    await lobby.assign_slot("player1", "A1")
    await lobby.assign_slot("player2", "B1")
    await lobby.set_ready("player1", True)
    # player2 not ready
    
    assert lobby.all_ready(min_players=2) is False


@pytest.mark.asyncio
async def test_ai_player(lobby):
    """Test adding AI player."""
    result = await lobby.add_player("ai1", "Bot", is_ai=True)
    assert result is True
    assert lobby.players["ai1"].is_ai is True
    assert lobby.players["ai1"].is_ready is True  # AI is always ready


@pytest.mark.asyncio
async def test_set_ai_level(lobby):
    """Test setting AI difficulty level."""
    await lobby.add_player("ai1", "Bot", is_ai=True)
    await lobby.assign_slot("ai1", "A1")
    
    result = await lobby.set_ai_level("A1", "predictive")
    assert result is True
    assert lobby.players["ai1"].ai_level == "predictive"


@pytest.mark.asyncio
async def test_set_ai_level_non_ai(lobby):
    """Test that setting AI level fails for human player."""
    await lobby.add_player("player1", "Alice", is_ai=False)
    await lobby.assign_slot("player1", "A1")
    
    result = await lobby.set_ai_level("A1", "predictive")
    assert result is False


@pytest.mark.asyncio
async def test_get_occupied_slots(lobby):
    """Test getting list of occupied slots."""
    await lobby.add_player("player1", "Alice")
    await lobby.add_player("player2", "Bob")
    await lobby.assign_slot("player1", "A1")
    await lobby.assign_slot("player2", "B3")
    
    occupied = lobby.get_occupied_slots()
    assert set(occupied) == {"A1", "B3"}


@pytest.mark.asyncio
async def test_get_team_slots(lobby):
    """Test getting slots for a specific team."""
    await lobby.add_player("player1", "Alice")
    await lobby.add_player("player2", "Bob")
    await lobby.add_player("player3", "Charlie")
    await lobby.assign_slot("player1", "A1")
    await lobby.assign_slot("player2", "A2")
    await lobby.assign_slot("player3", "B1")
    
    team_a = lobby.get_team_slots("A")
    team_b = lobby.get_team_slots("B")
    
    assert set(team_a) == {"A1", "A2"}
    assert set(team_b) == {"B1"}


@pytest.mark.asyncio
async def test_get_lobby_state(lobby):
    """Test getting lobby state as dictionary."""
    await lobby.add_player("player1", "Alice")
    await lobby.add_player("ai1", "Bot", is_ai=True)
    await lobby.assign_slot("player1", "A1")
    await lobby.assign_slot("ai1", "B1")
    await lobby.set_ready("player1", True)
    
    state = lobby.get_lobby_state()
    
    assert "slots" in state
    assert "ready_players" in state
    assert "settings" in state
    
    assert state["slots"]["A1"]["nickname"] == "Alice"
    assert state["slots"]["B1"]["is_ai"] is True
    assert "Alice" in state["ready_players"]
    assert "Bot" in state["ready_players"]  # AI is always ready


@pytest.mark.asyncio
async def test_reset_lobby(lobby):
    """Test resetting lobby to initial state."""
    await lobby.add_player("player1", "Alice")
    await lobby.assign_slot("player1", "A1")
    await lobby.set_ready("player1", True)
    
    lobby.reset()
    
    assert len(lobby.players) == 0
    assert all(slot_id is None for slot_id in lobby.slots.values())
    assert isinstance(lobby.settings, LobbySettings)


@pytest.mark.asyncio
async def test_lobby_settings():
    """Test lobby settings dataclass."""
    settings = LobbySettings(
        match_duration=300,
        goal_size=250,
        paddle_speed=8.0,
        ball_speed=5.0,
        max_score=10
    )
    
    assert settings.match_duration == 300
    assert settings.goal_size == 250
    assert settings.paddle_speed == 8.0
    assert settings.ball_speed == 5.0
    assert settings.max_score == 10

"""
Testy pro game_loop.py
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from multipong.network.server.game_loop import (
    GameLoop,
    run_game_loop,
    initialize_game_loop,
    get_game_loop
)
from multipong.engine.game_engine import MultipongEngine
from multipong.network.server.websocket_manager import WebSocketManager


class TestGameLoop:
    """Testy pro třídu GameLoop."""
    
    def test_init(self):
        """Test inicializace GameLoop."""
        engine = Mock(spec=MultipongEngine)
        manager = Mock(spec=WebSocketManager)
        
        loop = GameLoop(engine, manager, tick_rate=30)
        
        assert loop.engine is engine
        assert loop.manager is manager
        assert loop.tick_rate == 30
        assert loop.is_running is False
        assert loop.player_inputs == {}
    
    def test_init_with_default_tick_rate(self):
        """Test inicializace s výchozím tick rate z konfigurace."""
        engine = Mock(spec=MultipongEngine)
        manager = Mock(spec=WebSocketManager)
        
        loop = GameLoop(engine, manager)
        
        # Mělo by použít hodnotu z settings
        assert loop.tick_rate > 0
    
    def test_update_input(self):
        """Test aktualizace vstupů od hráče."""
        loop = GameLoop(Mock(), Mock())
        
        loop.update_input("A1", up=True, down=False)
        assert loop.player_inputs == {"A1": {"up": True, "down": False}}
        
        loop.update_input("A1", up=False, down=True)
        assert loop.player_inputs == {"A1": {"up": False, "down": True}}
        
        loop.update_input("B1", up=True, down=True)
        assert "B1" in loop.player_inputs
    
    def test_clear_input(self):
        """Test vymazání vstupů hráče."""
        loop = GameLoop(Mock(), Mock())
        
        loop.update_input("A1", up=True, down=False)
        loop.update_input("B1", up=False, down=True)
        
        loop.clear_input("A1")
        assert "A1" not in loop.player_inputs
        assert "B1" in loop.player_inputs
        
        # Vymazání neexistujícího hráče by nemělo způsobit chybu
        loop.clear_input("C1")
    
    def test_get_current_inputs(self):
        """Test získání kopie vstupů."""
        loop = GameLoop(Mock(), Mock())
        
        loop.update_input("A1", up=True, down=False)
        inputs = loop.get_current_inputs()
        
        assert inputs == {"A1": {"up": True, "down": False}}
        
        # Změna kopie by neměla ovlivnit originál
        inputs["A1"]["up"] = False
        assert loop.player_inputs["A1"]["up"] is True
    
    @pytest.mark.asyncio
    async def test_run_basic(self):
        """Test základního běhu game loop."""
        engine = Mock(spec=MultipongEngine)
        engine.update = Mock()
        engine.get_state = Mock(return_value={
            "ball": {"x": 100, "y": 200},
            "score": {"A": 0, "B": 0}
        })
        
        manager = AsyncMock(spec=WebSocketManager)
        manager.broadcast = AsyncMock(return_value=2)
        manager.get_player_count = Mock(return_value=2)
        
        loop = GameLoop(engine, manager, tick_rate=10)  # Nízký tick rate pro rychlý test
        
        # Spustíme loop na pozadí a zrušíme po krátké době
        task = asyncio.create_task(loop.run())
        await asyncio.sleep(0.3)  # Nechá proběhnout několik ticků
        loop.stop()
        
        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.CancelledError:
            pass
        
        # Ověříme, že engine a manager byly volány
        assert engine.update.call_count > 0
        assert engine.get_state.call_count > 0
        assert manager.broadcast.call_count > 0
    
    @pytest.mark.asyncio
    async def test_run_with_inputs(self):
        """Test běhu s aktuálními vstupy."""
        engine = Mock(spec=MultipongEngine)
        engine.update = Mock()
        engine.get_state = Mock(return_value={"score": {"A": 0, "B": 0}})
        
        manager = AsyncMock(spec=WebSocketManager)
        manager.broadcast = AsyncMock(return_value=1)
        manager.get_player_count = Mock(return_value=1)
        
        loop = GameLoop(engine, manager, tick_rate=10)
        loop.update_input("A1", up=True, down=False)
        
        task = asyncio.create_task(loop.run())
        await asyncio.sleep(0.2)
        loop.stop()
        
        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.CancelledError:
            pass
        
        # Ověříme že engine.update dostal správné vstupy
        assert engine.update.called
        # První volání mělo obsahovat naše vstupy
        first_call_args = engine.update.call_args_list[0][0][0]
        assert "A1" in first_call_args
    
    @pytest.mark.asyncio
    async def test_stop(self):
        """Test zastavení game loop."""
        engine = Mock(spec=MultipongEngine)
        engine.update = Mock()
        engine.get_state = Mock(return_value={})
        
        manager = AsyncMock(spec=WebSocketManager)
        manager.broadcast = AsyncMock(return_value=0)
        manager.get_player_count = Mock(return_value=0)
        
        loop = GameLoop(engine, manager, tick_rate=10)
        
        assert loop.is_running is False
        
        task = asyncio.create_task(loop.run())
        await asyncio.sleep(0.1)
        
        assert loop.is_running is True
        loop.stop()
        assert loop.is_running is False
        
        await asyncio.sleep(0.2)
        assert task.done()


class TestGameLoopGlobalAPI:
    """Testy pro globální API funkce."""
    
    def test_initialize_and_get_game_loop(self):
        """Test inicializace a získání globální instance."""
        engine = Mock(spec=MultipongEngine)
        manager = Mock(spec=WebSocketManager)
        
        loop = initialize_game_loop(engine, manager, tick_rate=30)
        
        assert loop is not None
        assert loop.tick_rate == 30
        
        # get_game_loop by mělo vrátit stejnou instanci
        retrieved = get_game_loop()
        assert retrieved is loop


class TestRunGameLoopFunction:
    """Testy pro funkční API run_game_loop."""
    
    @pytest.mark.asyncio
    async def test_run_game_loop_basic(self):
        """Test základního běhu funkčního API."""
        engine = Mock(spec=MultipongEngine)
        engine.update = Mock()
        engine.get_state = Mock(return_value={
            "ball": {"x": 100, "y": 200},
            "score": {"A": 0, "B": 0}
        })
        
        manager = AsyncMock(spec=WebSocketManager)
        manager.broadcast = AsyncMock(return_value=2)
        manager.get_player_count = Mock(return_value=2)
        
        player_inputs = {}
        
        # Spustíme na pozadí a zrušíme po krátké době
        task = asyncio.create_task(
            run_game_loop(engine, manager, player_inputs, tick_rate=10)
        )
        
        await asyncio.sleep(0.3)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Ověříme volání
        assert engine.update.call_count > 0
        assert engine.get_state.call_count > 0
        assert manager.broadcast.call_count > 0
    
    @pytest.mark.asyncio
    async def test_run_game_loop_with_inputs(self):
        """Test funkčního API se sdílenými vstupy."""
        engine = Mock(spec=MultipongEngine)
        engine.update = Mock()
        engine.get_state = Mock(return_value={"score": {"A": 0, "B": 0}})
        
        manager = AsyncMock(spec=WebSocketManager)
        manager.broadcast = AsyncMock(return_value=1)
        manager.get_player_count = Mock(return_value=1)
        
        # Sdílená mapa vstupů
        player_inputs = {"A1": {"up": True, "down": False}}
        
        task = asyncio.create_task(
            run_game_loop(engine, manager, player_inputs, tick_rate=10)
        )
        
        await asyncio.sleep(0.2)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Ověříme že engine dostal správné vstupy
        assert engine.update.called
        first_call_inputs = engine.update.call_args_list[0][0][0]
        assert first_call_inputs is player_inputs

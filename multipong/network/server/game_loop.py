"""
Game loop pro MULTIPONG server - asynchronní tick smyčka.
Řídí aktualizaci herního stavu a broadcast snapshots klientům.
"""

import asyncio
import logging
from typing import Dict, Any
from multipong.engine.game_engine import MultipongEngine
from multipong.network.server.websocket_manager import WebSocketManager
from multipong import settings

# Databázové operace (pro ukládání výsledků)
try:
    from api.db import SessionLocal
    from api import crud
    ENABLE_DB_LOGGING = True
except ImportError:
    ENABLE_DB_LOGGING = False


logger = logging.getLogger(__name__)


class GameLoop:
    """
    Asynchronní game loop pro server.
    
    Attributes:
        engine: Instance MultipongEngine
        manager: Instance WebSocketManager
        tick_rate: Frekvence aktualizací (Hz)
        is_running: Indikátor běžícího loopu
        player_inputs: Sdílená mapa vstupů od hráčů
    """
    
    def __init__(
        self,
        engine: MultipongEngine,
        manager: WebSocketManager,
        tick_rate: int = None
    ):
        """
        Inicializace game loop.
        
        Args:
            engine: Instance herního enginu
            manager: Instance WebSocket manageru
            tick_rate: Frekvence aktualizací v Hz (None = použije config)
        """
        self.engine = engine
        self.manager = manager
        self.tick_rate = tick_rate or settings.SERVER_TICK_RATE
        self.is_running = False
        
        # Sdílená mapa vstupů od hráčů {"player_id": {"up": bool, "down": bool}}
        self.player_inputs: Dict[str, Dict[str, bool]] = {}
        
        logger.info(f"🎮 GameLoop inicializován (tick rate: {self.tick_rate} Hz)")
    
    def update_input(self, player_id: str, up: bool, down: bool) -> None:
        """
        Aktualizuje vstup od konkrétního hráče.
        
        Args:
            player_id: ID hráče
            up: Stav tlačítka nahoru
            down: Stav tlačítka dolů
        """
        self.player_inputs[player_id] = {"up": up, "down": down}
    
    def clear_input(self, player_id: str) -> None:
        """
        Vymaže vstupy hráče (např. při odpojení).
        
        Args:
            player_id: ID hráče
        """
        if player_id in self.player_inputs:
            del self.player_inputs[player_id]
    
    def get_current_inputs(self) -> Dict[str, Dict[str, bool]]:
        """
        Vrátí aktuální snapshot vstupů.
        
        Returns:
            Kopie mapy vstupů (deep copy)
        """
        import copy
        return copy.deepcopy(self.player_inputs)
    
    async def run(self) -> None:
        """
        Spustí asynchronní game loop.
        
        Loop běží v cyklu:
        1. Sesbírá vstupy od hráčů
        2. Aktualizuje engine
        3. Získá snapshot stavu hry
        4. Broadcastuje snapshot všem klientům
        5. Čeká na další tick
        """
        self.is_running = True
        tick_interval = 1.0 / self.tick_rate
        tick_count = 0
        
        logger.info(f"🚀 Game loop spuštěn (interval: {tick_interval:.4f}s)")
        
        try:
            while self.is_running:
                tick_start = asyncio.get_event_loop().time()
                
                # 1. Aktualizace enginu s aktuálními vstupy
                self.engine.update(self.player_inputs)
                
                # 2. Získání kompletního stavu hry
                state = self.engine.get_state()
                
                # 3. Příprava snapshot zprávy pro klienty
                snapshot = {
                    "type": "snapshot",
                    **state
                }
                
                # 4. Broadcast snapshot všem připojeným hráčům
                sent_count = await self.manager.broadcast(snapshot)
                
                # Logování každých 60 ticků (1× za sekundu při 60 Hz)
                tick_count += 1
                if tick_count % 60 == 0:
                    logger.debug(
                        f"📊 Tick #{tick_count} | "
                        f"Hráči: {self.manager.get_player_count()} | "
                        f"Broadcast: {sent_count} | "
                        f"Score: {state.get('score', {})}"
                    )
                
                # 5. Čekání na další tick (kompenzace času zpracování)
                tick_end = asyncio.get_event_loop().time()
                elapsed = tick_end - tick_start
                sleep_time = max(0, tick_interval - elapsed)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    # Varování pokud zpracování trvá déle než tick interval
                    if tick_count % 60 == 0:  # Loguj jen občas
                        logger.warning(
                            f"⚠️ Tick #{tick_count} přesáhl interval: "
                            f"{elapsed:.4f}s > {tick_interval:.4f}s"
                        )
        
        except asyncio.CancelledError:
            logger.info("🛑 Game loop byl zrušen (CancelledError)")
            raise
        
        except Exception as e:
            logger.error(f"❌ Chyba v game loop: {e}", exc_info=True)
            raise
        
        finally:
            self.is_running = False
            logger.info(f"🏁 Game loop ukončen (celkem ticků: {tick_count})")
    
    def stop(self) -> None:
        """Zastaví game loop (nastaví flag, loop se ukončí na dalším ticku)."""
        logger.info("🛑 Zastavuji game loop...")
        self.is_running = False


# Globální instance pro snadné použití v serveru
_game_loop_instance: GameLoop | None = None


def initialize_game_loop(
    engine: MultipongEngine,
    manager: WebSocketManager,
    tick_rate: int = None
) -> GameLoop:
    """
    Inicializuje globální instanci game loop.
    
    Args:
        engine: Instance MultipongEngine
        manager: Instance WebSocketManager
        tick_rate: Volitelná frekvence ticků (Hz)
        
    Returns:
        Instance GameLoop
    """
    global _game_loop_instance
    _game_loop_instance = GameLoop(engine, manager, tick_rate)
    return _game_loop_instance


def get_game_loop() -> GameLoop | None:
    """
    Vrátí globální instanci game loop.
    
    Returns:
        Instance GameLoop nebo None pokud nebyla inicializována
    """
    return _game_loop_instance


async def run_game_loop(
    engine: MultipongEngine,
    manager: WebSocketManager,
    player_inputs: Dict[str, Dict[str, bool]],
    tick_rate: int = None
) -> None:
    """
    Funkční API pro spuštění game loop (dle Phase 4 dokumentace).
    
    Args:
        engine: Instance MultipongEngine
        manager: Instance WebSocketManager
        player_inputs: Sdílená mapa vstupů od hráčů
        tick_rate: Volitelná frekvence ticků v Hz (None = config)
    
    Example:
        ```python
        from multipong.engine import MultipongEngine
        from multipong.network.server import WebSocketManager
        from multipong.network.server.game_loop import run_game_loop
        
        engine = MultipongEngine()
        manager = WebSocketManager()
        inputs = {}  # Sdílená mapa
        
        # Spuštění v background tasku
        asyncio.create_task(run_game_loop(engine, manager, inputs))
        ```
    """
    tick_rate = tick_rate or settings.SERVER_TICK_RATE
    tick_interval = 1.0 / tick_rate
    tick_count = 0
    
    logger.info(f"🚀 run_game_loop spuštěn (tick rate: {tick_rate} Hz)")
    
    try:
        while True:
            # 1. Aktualizace enginu s aktuálními vstupy
            engine.update(player_inputs)
            
            # 2. Získání stavu hry
            state = engine.get_state()
            
            # 3. Příprava a broadcast snapshot
            snapshot = {
                "type": "snapshot",
                **state
            }
            
            await manager.broadcast(snapshot)
            
            # 4. Čekání na další tick
            tick_count += 1
            if tick_count % 60 == 0:
                logger.debug(
                    f"📊 Tick #{tick_count} | "
                    f"Hráči: {manager.get_player_count()} | "
                    f"Score: {state.get('score', {})}"
                )
            
            await asyncio.sleep(tick_interval)
    
    except asyncio.CancelledError:
        logger.info("🛑 run_game_loop byl zrušen (CancelledError)")
        raise
    
    except Exception as e:
        logger.error(f"❌ Chyba v run_game_loop: {e}", exc_info=True)
        raise


def save_match_results(engine: MultipongEngine, duration_seconds: int) -> None:
    """
    Uloží výsledky skončeného zápasu do databáze.
    
    Args:
        engine: Instance herního enginu s konečnými výsledky
        duration_seconds: Doba trvání zápasu v sekundách
    """
    if not ENABLE_DB_LOGGING:
        logger.warning("⚠️ Databáze není dostupná - výsledky se neukládají")
        return
    
    db = None
    try:
        db = SessionLocal()
        
        # 1. Vytvoříme zápas
        match = crud.create_match(
            db,
            team_left_score=engine.team_left.score,
            team_right_score=engine.team_right.score,
            duration_seconds=duration_seconds
        )
        
        # 2. Přidáme statistiky všech hráčů
        all_paddles = engine.team_left.paddles + engine.team_right.paddles
        
        for paddle in all_paddles:
            # Zajistíme, že hráč existuje v databázi
            player = crud.get_or_create_player(db, paddle.player_id, paddle.stats.team)
            
            # Přidáme statistiku za tento zápas
            crud.add_player_stats(
                db,
                match_id=match.id,
                player_id=paddle.player_id,
                hits=paddle.stats.hits,
                goals_scored=paddle.stats.goals_scored,
                goals_received=paddle.stats.goals_received
            )
        
        logger.info(f"✅ Výsledky zápasu uloženy (match_id={match.id})")
        
    except Exception as e:
        logger.error(f"❌ Chyba při ukládání výsledků: {e}", exc_info=True)
    
    finally:
        if db:
            db.close()

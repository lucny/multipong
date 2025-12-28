"""
WebSocket server pro MULTIPONG - Phase 4
Základní implementace s FastAPI + WebSocket endpointy.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from .player_session import PlayerSession
from .websocket_manager import WebSocketManager
from .lobby_manager import LobbyManager
from multipong.engine.game_engine import MultipongEngine
from multipong.network.server.game_loop import run_game_loop
from multipong import settings

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Seznam background tasků pro úklid při shutdownu
_background_tasks: list[asyncio.Task] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Spuštění a korektní ukončení background smyček bez deprecated on_event."""
    logger.info("🚀 Spouštím MULTIPONG WebSocket server...")
    logger.info(f"🎮 Lobby stav: {lobby.get_lobby_status()}")

    # Aktivuj engine (reset míčku, zapne běh)
    try:
        engine.start()
        logger.info("🎯 Engine start() dokončen")
    except Exception as e:
        logger.error(f"❌ Chyba při startu enginu: {e}")

    # Spustit timeout checker
    _background_tasks.append(asyncio.create_task(timeout_checker()))
    logger.info("⏱️ Timeout checker aktivován (10s timeout)")

    # Průběžná synchronizace vstupů z WebSocketManageru do sdílené mapy
    async def _sync_inputs_loop():
        while True:
            await asyncio.sleep(0.01)  # ~100 Hz refresh vstupů
            try:
                inputs = manager.collect_inputs()
                _shared_player_inputs.clear()
                _shared_player_inputs.update(inputs)
            except Exception as e:
                logger.error(f"❌ Chyba při synchronizaci vstupů: {e}")

    _background_tasks.append(asyncio.create_task(_sync_inputs_loop()))
    logger.info("🎛️ Sync input loop spuštěn")

    try:
        yield
    finally:
        logger.info("🛑 Shutting down background tasks...")
        for task in _background_tasks:
            task.cancel()
        if _background_tasks:
            await asyncio.gather(*_background_tasks, return_exceptions=True)
        _background_tasks.clear()


# FastAPI aplikace
app = FastAPI(
    title="MULTIPONG WebSocket Server",
    description="Server pro multiplayerový MULTIPONG (Phase 4)",
    version="0.4.0",
    lifespan=lifespan,
)

# Globální instance manažerů
manager = WebSocketManager()
lobby = LobbyManager()

# Herní engine a sdílená mapa vstupů pro game loop
engine = MultipongEngine(
    arena_width=settings.WINDOW_WIDTH,
    arena_height=settings.WINDOW_HEIGHT,
    num_players_per_team=settings.PADDLES_COUNT_PER_TEAM
)
_shared_player_inputs: Dict[str, Dict[str, bool]] = {}


@app.get("/")
async def root():
    """Základní info endpoint."""
    return {
        "name": "MULTIPONG WebSocket Server",
        "version": "0.4.0",
        "phase": 4,
        "websocket_endpoint": "/ws/{player_id}"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint pro monitoring."""
    return {"status": "healthy"}


@app.get("/lobby/status")
async def lobby_status():
    """Vrátí aktuální stav lobby."""
    return lobby.get_lobby_status()


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    """
    WebSocket endpoint pro připojení hráče.
    
    Args:
        websocket: WebSocket spojení
        player_id: ID hráče (např. "A1", "A2", "B1", "B2") nebo "auto" pro automatické přidělení
    
    Protokol zpráv od klienta:
        {
            "type": "input",
            "player_id": "A1",
            "up": true,
            "down": false
        }
        {
            "type": "chat",
            "player_id": "A1",
            "message": "Hello!"
        }
    """
    await websocket.accept()
    
    # Přidělení pozice v lobby
    assigned_slot = None
    if player_id.lower() == "auto":
        assigned_slot = lobby.assign_slot()
    else:
        assigned_slot = lobby.assign_slot(player_id)
    
    if assigned_slot is None:
        logger.error(f"❌ Nelze přidělit pozici pro {player_id}")
        await websocket.send_json({
            "type": "error",
            "message": "No available slots in lobby"
        })
        await websocket.close()
        return
    
    # Vytvoření session s přidělenou pozicí
    session = PlayerSession(websocket, assigned_slot)
    await manager.add(session)
    
    logger.info(f"🟢 Hráč {assigned_slot} připojen (původní ID: {player_id})")
    
    # Odeslání potvrzení o připojení
    await session.send_json({
        "type": "connected",
        "assigned_slot": assigned_slot,
        "lobby_status": lobby.get_lobby_status()
    })
    
    try:
        while True:
            # Příjem zprávy od klienta
            data = await websocket.receive_json()
            
            # Aktualizace aktivity
            session.update_activity()
            
            # Logování přijaté zprávy
            msg_type = data.get("type", "unknown")
            logger.info(f"📨 [{assigned_slot}] Přijato: {msg_type}")
            logger.debug(f"    Data: {data}")
            
            # Zpracování podle typu zprávy
            if msg_type == "input":
                up = data.get("up", False)
                down = data.get("down", False)
                session.update_input(up, down)
                logger.info(f"    ⬆️ UP: {up}, ⬇️ DOWN: {down}")
                
            elif msg_type == "ping":
                logger.debug(f"    💓 Ping od {assigned_slot}")
                pong_msg = {"type": "pong"}
                ping_id = data.get("ping_id")
                if ping_id:
                    pong_msg["ping_id"] = ping_id
                await session.send_json(pong_msg)
                
            elif msg_type == "chat":
                message = data.get("message", "")
                logger.info(f"    💬 Chat: {message}")
                
                # Broadcast chat zprávy všem hráčům
                chat_broadcast = {
                    "type": "chat",
                    "player_id": assigned_slot,
                    "message": message
                }
                sent_count = await manager.broadcast(chat_broadcast)
                logger.info(f"    📡 Chat rozeslán {sent_count} hráčům")
                
            else:
                logger.warning(f"    ⚠️ Neznámý typ zprávy: {msg_type}")
    
    except WebSocketDisconnect:
        logger.info(f"🔴 Hráč {assigned_slot} odpojen (WebSocketDisconnect)")
    
    except Exception as e:
        logger.error(f"❌ Chyba při komunikaci s {assigned_slot}: {e}", exc_info=True)
    
    finally:
        # Uvolnění pozice v lobby
        lobby.release_slot(assigned_slot)
        await manager.remove(session)
        logger.info(f"🔌 Ukončeno spojení s hráčem {assigned_slot}")


async def timeout_checker():
    """
    Periodická kontrola timeoutu hráčů.
    Odpojí hráče, kteří neposlali zprávu po dobu 10 sekund.
    """
    while True:
        await asyncio.sleep(5)  # Kontrola každých 5 sekund
        disconnected = await manager.disconnect_inactive(timeout_seconds=10.0)
        if disconnected > 0:
            logger.warning(f"⏱️ Odpojeno {disconnected} neaktivních hráčů")


    # Spustit hlavní game loop (broadcast snapshotů)
    asyncio.create_task(run_game_loop(engine, manager, _shared_player_inputs))
    logger.info("🎮 Game loop spuštěn")


@app.get("/test-client")
async def test_client():
    """
    Jednoduchá HTML stránka pro test WebSocket připojení.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MULTIPONG WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .controls { margin: 20px 0; }
            button { padding: 10px 20px; margin: 5px; font-size: 16px; }
            #log { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: auto; }
            .log-entry { margin: 5px 0; }
        </style>
    </head>
    <body>
        <h1>🏓 MULTIPONG WebSocket Test Client</h1>
        
        <div class="controls">
            <label>Player ID: 
                <input type="text" id="playerId" value="A1" />
            </label>
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
        </div>
        
        <div class="controls">
            <button onmousedown="sendInput(true, false)" onmouseup="sendInput(false, false)">⬆️ UP</button>
            <button onmousedown="sendInput(false, true)" onmouseup="sendInput(false, false)">⬇️ DOWN</button>
            <button onclick="sendPing()">💓 Ping</button>
        </div>
        
        <div class="controls">
            <label>Chat: 
                <input type="text" id="chatMessage" placeholder="Type message..." />
            </label>
            <button onclick="sendChat()">📨 Send</button>
        </div>
        
        <h3>Log:</h3>
        <div id="log"></div>
        
        <script>
            let ws = null;
            
            function log(message) {
                const logDiv = document.getElementById('log');
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
                logDiv.appendChild(entry);
                logDiv.scrollTop = logDiv.scrollHeight;
            }
            
            function connect() {
                const playerId = document.getElementById('playerId').value;
                ws = new WebSocket(`ws://localhost:8000/ws/${playerId}`);
                
                ws.onopen = () => {
                    log(`✅ Připojeno jako ${playerId}`);
                };
                
                ws.onmessage = (event) => {
                    log(`📨 Přijato: ${event.data}`);
                };
                
                ws.onclose = () => {
                    log('🔴 Odpojeno');
                };
                
                ws.onerror = (error) => {
                    log(`❌ Chyba: ${error}`);
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function sendInput(up, down) {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const playerId = document.getElementById('playerId').value;
                    const msg = {
                        type: 'input',
                        player_id: playerId,
                        up: up,
                        down: down
                    };
                    ws.send(JSON.stringify(msg));
                    log(`⬆️${up ? '✓' : '✗'} ⬇️${down ? '✓' : '✗'}`);
                }
            }
            
            function sendPing() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'ping' }));
                    log('💓 Ping odesláno');
                }
            }
            
            function sendChat() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = document.getElementById('chatMessage').value;
                    if (message.trim()) {
                        ws.send(JSON.stringify({ 
                            type: 'chat',
                            message: message 
                        }));
                        log(`💬 Chat sent: ${message}`);
                        document.getElementById('chatMessage').value = '';
                    }
                }
            }
            
            // Enter key pro odeslání chatu
            document.addEventListener('DOMContentLoaded', () => {
                document.getElementById('chatMessage').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendChat();
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


if __name__ == "__main__":
    # Pro lokální vývoj
    import uvicorn
    logger.info("🚀 Spouštím MULTIPONG WebSocket server...")
    uvicorn.run(
        "websocket_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

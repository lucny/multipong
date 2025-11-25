# MULTIPONG WebSocket Server

WebSocket server pro multiplayerový MULTIPONG (Phase 4).

## 🚀 Spuštění serveru

### Varianta 1: Přímé spuštění souboru

```powershell
python multipong/network/server/websocket_server.py
```

### Varianta 2: Uvicorn (doporučeno pro produkci)

```powershell
uvicorn multipong.network.server.websocket_server:app --reload --host 0.0.0.0 --port 8000
```

## 📡 Endpoints

### HTTP Endpoints

- `GET /` - Základní informace o serveru
- `GET /health` - Health check
- `GET /test-client` - Interaktivní testovací klient v prohlížeči

### WebSocket Endpoint

- `WS /ws/{player_id}` - WebSocket připojení pro hráče

Příklad: `ws://localhost:8000/ws/A1`

## 🧪 Testování

### 1. Test v prohlížeči

Otevři v prohlížeči: http://localhost:8000/test-client

### 2. Test přes Python websockets

```python
import asyncio
import websockets
import json

async def test_client():
    async with websockets.connect("ws://localhost:8000/ws/A1") as ws:
        # Poslat input
        await ws.send(json.dumps({
            "type": "input",
            "player_id": "A1",
            "up": True,
            "down": False
        }))
        
        # Poslat ping
        await ws.send(json.dumps({"type": "ping"}))

asyncio.run(test_client())
```

## 📨 Protokol zpráv

### Klient → Server

#### Input zpráva
```json
{
  "type": "input",
  "player_id": "A1",
  "up": true,
  "down": false
}
```

#### Ping zpráva
```json
{
  "type": "ping"
}
```

#### Chat zpráva
```json
{
  "type": "chat",
  "message": "Hello!"
}
```

## 📝 Poznámky k aktuální implementaci

Tato verze zatím **pouze přijímá a loguje zprávy**, neposílá odpovědi zpět.

V další fázi bude přidáno:
- ✅ Broadcast snapshots (stav hry)
- ✅ Game loop (60 Hz tick)
- ✅ PlayerSession management
- ✅ WebSocketManager
- ✅ Integrace s MultipongEngine

## 🔍 Logování

Server loguje všechny příchozí zprávy:
- `📨` Přijaté zprávy
- `🟢` Nové připojení
- `🔴` Odpojení
- `⚠️` Varování
- `❌` Chyby

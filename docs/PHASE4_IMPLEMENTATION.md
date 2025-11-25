# WebSocket Server - Phase 4 Implementation

## ✅ Co bylo implementováno

### 1. FastAPI WebSocket Server (`websocket_server.py`)

**Funkce:**
- ✅ FastAPI aplikace s WebSocket podporou
- ✅ Endpoint `/ws/{player_id}` pro připojení hráčů
- ✅ Příjem a logování zpráv od klientů
- ✅ Podpora různých typů zpráv (input, ping, chat)
- ✅ Health check endpoint `/health`
- ✅ Informační endpoint `/`
- ✅ Integrovaný test klient `/test-client` (HTML + JavaScript)

**Protokol zpráv (klient → server):**

```json
// Input zpráva
{
  "type": "input",
  "player_id": "A1",
  "up": true,
  "down": false
}

// Ping zpráva
{
  "type": "ping"
}

// Chat zpráva
{
  "type": "chat",
  "message": "Hello!"
}
```

**Logování:**
- 🟢 Nové připojení hráče
- 📨 Příchozí zprávy s detaily
- 🔴 Odpojení hráče
- ⚠️ Varování (neznámý typ zprávy)
- ❌ Chyby při komunikaci

### 2. Test Klient (`test_websocket_client.py`)

Python asyncio klient pro testování serveru bez prohlížeče.

### 3. Spouštěcí skripty

- `start_server.bat` - Windows batch skript
- `start_server.ps1` - PowerShell skript

## 🚀 Jak spustit

### Metoda 1: PowerShell skript (doporučeno)

```powershell
.\start_server.ps1
```

### Metoda 2: Batch soubor

```cmd
start_server.bat
```

### Metoda 3: Přímý příkaz

```powershell
D:/projekty/multipong/.venv/Scripts/python.exe -m uvicorn multipong.network.server.websocket_server:app --host 0.0.0.0 --port 8000 --reload
```

### Metoda 4: Python modul

```powershell
D:/projekty/multipong/.venv/Scripts/python.exe multipong/network/server/websocket_server.py
```

## 🧪 Testování

### 1. Webový test klient

Otevři v prohlížeči: <http://localhost:8000/test-client>

- Zadej Player ID (např. "A1")
- Klikni "Connect"
- Testuj tlačítka UP/DOWN/Ping
- Sleduj log zpráv

### 2. Python test klient

```powershell
D:/projekty/multipong/.venv/Scripts/python.exe multipong/network/server/test_websocket_client.py
```

### 3. Manuální test přes websockets knihovnu

```python
import asyncio
import websockets
import json

async def test():
    async with websockets.connect("ws://localhost:8000/ws/A1") as ws:
        # Pošli input
        await ws.send(json.dumps({
            "type": "input",
            "player_id": "A1",
            "up": True,
            "down": False
        }))
        
        # Čekej chvíli
        await asyncio.sleep(1)

asyncio.run(test())
```

## 📊 Kontrola logů serveru

Server loguje všechny události:

```
2025-11-25 12:00:00 - __main__ - INFO - 🟢 Hráč A1 připojen
2025-11-25 12:00:01 - __main__ - INFO - 📨 [A1] Přijato: input
2025-11-25 12:00:01 - __main__ - INFO -     ⬆️ UP: True, ⬇️ DOWN: False
2025-11-25 12:00:05 - __main__ - INFO - 🔴 Hráč A1 odpojen (WebSocketDisconnect)
```

## 📝 Co zatím NENÍ implementováno

Podle Phase 4 dokumentace ještě chybí:

- ⏳ `PlayerSession` class
- ⏳ `WebSocketManager` class  
- ⏳ `game_loop.py` s tick smyčkou (60 Hz)
- ⏳ Integrace s `MultipongEngine`
- ⏳ Broadcast snapshots zpět klientům
- ⏳ Správa vstupů od více hráčů současně

**Aktuální implementace splňuje požadavek:** "Zatím jen přijímej a loguj zprávy od klienta, nic nereaguj zpět."

## 🔄 Další kroky (Phase 4 pokračování)

1. Vytvořit `player_session.py` s třídou `PlayerSession`
2. Vytvořit `websocket_manager.py` s třídou `WebSocketManager`
3. Vytvořit `game_loop.py` s asynchronní tick smyčkou
4. Integrovat `MultipongEngine` do serveru
5. Implementovat broadcast snapshots
6. Přidat lobby systém pro přidělování hráčů

## 🐛 Troubleshooting

### Server se nespustí - ModuleNotFoundError

Ujisti se, že máš aktivované virtuální prostředí:

```powershell
.venv\Scripts\Activate.ps1
```

Nebo použij plnou cestu k Python:

```powershell
D:/projekty/multipong/.venv/Scripts/python.exe
```

### Port 8000 již používán

Změň port v příkazu:

```powershell
uvicorn multipong.network.server.websocket_server:app --port 8001
```

### Test klient se nemůže připojit

1. Zkontroluj, že server běží: <http://localhost:8000>
2. Zkontroluj firewall
3. Použij `127.0.0.1` místo `localhost`

## 📚 Reference

- FastAPI WebSocket dokumentace: <https://fastapi.tiangolo.com/advanced/websockets/>
- Python websockets: <https://websockets.readthedocs.io/>
- Uvicorn dokumentace: <https://www.uvicorn.org/>

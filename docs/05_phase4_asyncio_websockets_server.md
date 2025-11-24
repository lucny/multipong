# **05_phase4_asyncio_websockets_server.md — Návrh WebSocket serveru (asyncio)**

## 🎯 1. Cíle fáze 4

V této fázi začneme stavět **síťovou vrstvu** MULTIPONGU.
Hra se díky tomu stane:

* **multiplayerovou**
* **synchronizovanou** mezi klienty
* **server-autoritatvní** (server rozhoduje, klient jen ovládá)
* **asynchronně řízenou** (asyncio)

Konkrétně vytvoříme:

* základní WebSocket server (FastAPI nebo čisté asyncio)
* asynchronní tick loop (herní smyčka běžící na serveru)
* systém hráčských relací (`PlayerSession`)
* protokol pro přenos dat (input → snapshot)
* napojení na `MultipongEngine` z předchozí fáze

---

# 🧠 2. Proč přesunout engine na server?

Aby šlo MULTIPONG hrát v síti, logika hry musí běžet **jen na jednom místě** – na serveru.
Klienti pouze:

* posílají vstupy (nahoru/dolů)
* přijímají snapshoty stavu hry
* vykreslují je v Pygame

Tento přístup:

✔ eliminuje cheatování
✔ zaručuje synchronizaci
✔ usnadňuje vývoj AI
✔ umožní zápisy výsledků do DB

---

# 🏗 3. Architektura serverové vrstvy

```
          ┌─────────────────────────────┐
          │         WebSocket Server     │
          │  (FastAPI nebo asyncio.ws)  │
          └──────────────┬──────────────┘
                         ws
                          │
                          ▼
                 ┌──────────────────┐
                 │ PlayerSession(s) │
                 └───────┬──────────┘
                         │ (inputy)
                         ▼
                ┌────────────────────┐
                │   MultipongEngine  │
                │ (autorita, logika) │
                └───────┬────────────┘
                         │ (snapshoty)
                         ▼
              ┌────────────────────────┐
              │  Broadcast all players │
              └────────────────────────┘
```

---

# 🧩 4. Asynchronní tick smyčka

Serverová smyčka běží např. **60× za sekundu**:

1. sesbírá inputy od hráčů
2. zavolá `engine.update(inputy)`
3. vyrobí snapshot
4. rozešle snapshot všem klientům

Ukázková smyčka:

```python
async def game_loop():
    while True:
        engine.update(collected_inputs)
        state = engine.get_state()

        await websocket_manager.broadcast(state)

        await asyncio.sleep(1/60)   # 60 Hz
```

---

# 🟦 5. Komunikační protokol (JSON)

## 5.1 Klient → Server (input)

```json
{
  "type": "input",
  "player_id": "A2",
  "up": true,
  "down": false
}
```

## 5.2 Server → Klient (snapshot)

```json
{
  "type": "snapshot",
  "ball": { "x": 620, "y": 430, "radius": 10 },
  "team_left": { "score": 2, "paddles": [...] },
  "team_right": { "score": 3, "paddles": [...] },
  "goal_left": {"top": 300, "bottom": 500},
  "goal_right": {"top": 300, "bottom": 500}
}
```

---

# 🟩 6. Návrh souborů pro server

Vytvoříme novou sekci projektu:

```
multipong/
│
├── multipong/
│     ├── network/
│     │     ├── server/
│     │     │     ├── websocket_server.py
│     │     │     ├── player_session.py
│     │     │     ├── websocket_manager.py
│     │     │     └── game_loop.py
│     │     └── client/
│     │           ├── ws_client.py
│     │           └── message_decoder.py
│     └── engine/
│
└── docs/
```

---

# 🟥 7. Třída `PlayerSession`

Uchovává:

* WebSocket spojení s hráčem
* ID hráče (`A1`, `A2`, `B1`…)
* poslední input

`soubor: multipong/network/server/player_session.py`

```python
class PlayerSession:
    def __init__(self, websocket, player_id):
        self.websocket = websocket
        self.player_id = player_id
        self.current_input = {"up": False, "down": False}
```

---

# 🟧 8. Třída `WebSocketManager`

Spravuje všechny připojené hráče:

```python
class WebSocketManager:
    def __init__(self):
        self.sessions = {}   # {player_id: PlayerSession}

    async def add(self, session):
        self.sessions[session.player_id] = session

    async def remove(self, session):
        if session.player_id in self.sessions:
            del self.sessions[session.player_id]

    async def broadcast(self, message):
        for session in list(self.sessions.values()):
            await session.websocket.send_json(message)
```

---

# 🟦 9. WebSocket server (FastAPI verze)

`soubor: websocket_server.py`

```python
import asyncio
from fastapi import FastAPI, WebSocket
from .player_session import PlayerSession
from .websocket_manager import WebSocketManager
from ...engine.multipong_engine import MultipongEngine

app = FastAPI()
manager = WebSocketManager()
engine = MultipongEngine()

# hráčské vstupy typu { "A1": {"up":false,"down":true}, ... }
inputs = {}

@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    await websocket.accept()

    session = PlayerSession(websocket, player_id)
    await manager.add(session)

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "input":
                inputs[player_id] = {
                    "up": data["up"],
                    "down": data["down"]
                }

    except:
        await manager.remove(session)
```

---

# 🟩 10. Tic smyčka serveru

`soubor: game_loop.py`

```python
async def run_game_loop():
    while True:
        engine.update(inputs)
        state = engine.get_state()
        await manager.broadcast({"type": "snapshot", **state})
        await asyncio.sleep(1/60)
```

Spustíme loop při startu serveru:

```python
import asyncio
from .websocket_server import app
from .game_loop import run_game_loop

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_game_loop())
```

---

# 🔌 11. Spuštění serveru

Použijeme Uvicorn:

```
uvicorn multipong.network.server.websocket_server:app --reload
```

---

# 🎮 12. Test komunikace

Studenti si mohou napsat minikonzoli:

```python
import websockets
import asyncio
import json

async def test():
    async with websockets.connect("ws://localhost:8000/ws/A1") as ws:
        await ws.send(json.dumps({"type": "input", "up":True, "down":False}))
        print(await ws.recv())

asyncio.run(test())
```

---

# 🧪 13. Domácí mini výzvy pro studenty

### 🔹 1) Ošetři timeout

Odpojit hráče, který nic neposlal 10 sekund.

### 🔹 2) Přidej „lobby“ systém

Hráč se připojí → server mu přidělí volnou pálku.

### 🔹 3) Přidej chat zprávy

Zpráva `"type": "chat"` → broadcast hráčům.

### 🔹 Copilot prompt

> „Jak mohu do WebSocketManager přidat heartbeat mechanismus, který klientům odesílá keep-alive zprávy každých 5 sekund?“



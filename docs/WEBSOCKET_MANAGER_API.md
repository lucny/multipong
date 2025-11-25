# PlayerSession a WebSocketManager - Dokumentace

## ✅ Implementované třídy

### 1. `PlayerSession` (`player_session.py`)

Reprezentuje jednoho připojeného hráče.

#### Atributy:
- `websocket: WebSocket` - WebSocket spojení s klientem
- `player_id: str` - Unikátní ID hráče (např. "A1", "A2", "B1")
- `current_input: Dict[str, bool]` - Aktuální stav vstupů `{"up": bool, "down": bool}`
- `is_connected: bool` - Indikátor aktivního připojení

#### Metody:

```python
# Inicializace
session = PlayerSession(websocket, "A1")

# Aktualizace vstupů od hráče
session.update_input(up=True, down=False)

# Získání kopie vstupů
inputs = session.get_input()  # {'up': True, 'down': False}

# Odeslání JSON zprávy klientovi
await session.send_json({"type": "snapshot", "data": {...}})

# Odpojení session
session.disconnect()
```

### 2. `WebSocketManager` (`websocket_manager.py`)

Správce všech aktivních WebSocket připojení.

#### Atributy:
- `sessions: Dict[str, PlayerSession]` - Slovník aktivních relací

#### Základní metody:

```python
# Vytvoření manageru
manager = WebSocketManager()

# Přidání hráče
await manager.add(session)  # Returns: bool

# Odebrání hráče
await manager.remove(session)  # Returns: bool
await manager.remove_by_id("A1")  # Returns: bool

# Získání session
session = manager.get_session("A1")  # Returns: PlayerSession | None

# Statistiky
count = manager.get_player_count()  # Returns: int
player_ids = manager.get_player_ids()  # Returns: List[str]
sessions = manager.get_all_sessions()  # Returns: List[PlayerSession]
```

#### Broadcast metody:

```python
# Broadcast všem hráčům
message = {"type": "snapshot", "ball": {...}}
sent_count = await manager.broadcast(message)

# Broadcast s vyloučením
sent_count = await manager.broadcast(message, exclude=["A1", "B2"])

# Broadcast pouze jednomu týmu
sent_count = await manager.broadcast_to_team(message, "A")  # Pouze tým A
```

#### Utility metody:

```python
# Sesbírání všech vstupů
inputs = manager.collect_inputs()
# Returns: {"A1": {"up": True, "down": False}, "B1": {...}, ...}

# Odpojení všech hráčů
await manager.disconnect_all()
```

## 📝 Příklady použití

### Základní workflow ve WebSocket serveru

```python
from fastapi import FastAPI, WebSocket
from multipong.network.server import PlayerSession, WebSocketManager

app = FastAPI()
manager = WebSocketManager()

@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    await websocket.accept()
    
    # Vytvoř a přidej session
    session = PlayerSession(websocket, player_id)
    await manager.add(session)
    
    try:
        while True:
            # Příjem zprávy
            data = await websocket.receive_json()
            
            # Aktualizace vstupů
            if data["type"] == "input":
                session.update_input(
                    up=data.get("up", False),
                    down=data.get("down", False)
                )
    except:
        # Odebrání při odpojení
        await manager.remove(session)
```

### Game loop s broadcast

```python
import asyncio

async def game_loop(engine, manager):
    while True:
        # Sesbírání vstupů od všech hráčů
        inputs = manager.collect_inputs()
        
        # Aktualizace enginu
        engine.update(inputs)
        
        # Získání stavu hry
        state = engine.get_state()
        
        # Broadcast snapshot všem hráčům
        await manager.broadcast({
            "type": "snapshot",
            **state
        })
        
        # 60 Hz tick rate
        await asyncio.sleep(1/60)
```

### Filtrované zprávy

```python
# Zpráva pouze pro tým A
await manager.broadcast_to_team(
    {"type": "team_message", "text": "Go team A!"},
    "A"
)

# Zpráva všem kromě odesílatele
sender_id = "A1"
await manager.broadcast(
    {"type": "chat", "from": sender_id, "message": "Hello!"},
    exclude=[sender_id]
)
```

## 🧪 Testování

### Spuštění unit testů

```powershell
pytest tests/network/test_websocket_manager.py -v
```

Celkem **22 testů** pokrývajících:
- ✅ PlayerSession inicializaci, vstupy, odeslání zpráv
- ✅ WebSocketManager přidání/odebrání sessions
- ✅ Broadcast všem, s vyloučením, pouze týmu
- ✅ Sesbírání vstupů
- ✅ Odpojení všech hráčů

### Demo příklad

```powershell
python -m multipong.network.server.demo_manager
```

## 📊 API Reference

### PlayerSession

| Metoda | Parametry | Návratová hodnota | Popis |
|--------|-----------|-------------------|-------|
| `__init__` | `websocket, player_id` | - | Inicializace session |
| `update_input` | `up: bool, down: bool` | `None` | Aktualizace vstupů |
| `get_input` | - | `Dict[str, bool]` | Získání kopie vstupů |
| `send_json` | `data: dict` | `None` (async) | Odeslání JSON zprávy |
| `disconnect` | - | `None` | Označení jako odpojená |

### WebSocketManager

| Metoda | Parametry | Návratová hodnota | Popis |
|--------|-----------|-------------------|-------|
| `add` | `session: PlayerSession` | `bool` (async) | Přidání session |
| `remove` | `session: PlayerSession` | `bool` (async) | Odebrání session |
| `remove_by_id` | `player_id: str` | `bool` (async) | Odebrání podle ID |
| `get_session` | `player_id: str` | `PlayerSession \| None` | Získání session |
| `get_all_sessions` | - | `List[PlayerSession]` | Všechny sessions |
| `get_player_ids` | - | `List[str]` | Seznam player IDs |
| `get_player_count` | - | `int` | Počet hráčů |
| `broadcast` | `message: dict, exclude: List[str]` | `int` (async) | Broadcast všem |
| `broadcast_to_team` | `message: dict, team: str` | `int` (async) | Broadcast týmu |
| `collect_inputs` | - | `Dict[str, Dict]` | Vstupy od všech |
| `disconnect_all` | - | `None` (async) | Odpojení všech |

## 🔍 Logování

Obě třídy používají Python `logging` modul:

```
INFO - ✅ Přidán hráč A1 (celkem hráčů: 1)
INFO - ❌ Odebrán hráč A2 (zbývá hráčů: 0)
WARNING - Hráč A1 je již připojen, odmítám duplicitní připojení
ERROR - Chyba při odesílání zprávy hráči A1: ...
```

## 🚀 Další kroky (Phase 4)

Co zbývá implementovat:
- ⏳ Integrace s `MultipongEngine`
- ⏳ `game_loop.py` s asynchronní tick smyčkou (60 Hz)
- ⏳ Aktualizace `websocket_server.py` pro použití těchto tříd
- ⏳ Lobby systém pro automatické přidělování slotů
- ⏳ Heartbeat / keep-alive mechanismus

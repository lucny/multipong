# Game Loop - Dokumentace

## ✅ Implementace

Vytvořena asynchronní game loop pro MULTIPONG server podle Phase 4 specifikace.

## 📁 Soubory

- **`multipong/network/server/game_loop.py`** - Implementace game loop
- **`tests/network/test_game_loop.py`** - Unit testy (11 testů)
- **`multipong/network/server/demo_game_loop.py`** - Demo příklady

## 🎯 Hlavní funkce

### 1. `GameLoop` třída

Objektově orientované API pro správu game loop.

```python
from multipong.engine import MultipongEngine
from multipong.network.server import WebSocketManager, GameLoop

# Vytvoření komponenty
engine = MultipongEngine()
manager = WebSocketManager()

# Vytvoření game loop
loop = GameLoop(engine, manager, tick_rate=60)

# Aktualizace vstupů od hráčů
loop.update_input("A1", up=True, down=False)
loop.update_input("B1", up=False, down=True)

# Spuštění loop (asynchronní)
await loop.run()

# Zastavení
loop.stop()
```

#### Metody GameLoop:

| Metoda | Popis |
|--------|-------|
| `__init__(engine, manager, tick_rate)` | Inicializace loop |
| `update_input(player_id, up, down)` | Aktualizace vstupů hráče |
| `clear_input(player_id)` | Vymazání vstupů hráče |
| `get_current_inputs()` | Získání kopie všech vstupů |
| `run()` | Spuštění loop (async) |
| `stop()` | Zastavení loop |

### 2. `run_game_loop()` funkce

Funkční API pro přímé spuštění (podle Phase 4 dokumentace).

```python
from multipong.network.server import run_game_loop

# Sdílená mapa vstupů
player_inputs = {
    "A1": {"up": True, "down": False},
    "B1": {"up": False, "down": False}
}

# Spuštění (jako background task)
asyncio.create_task(
    run_game_loop(engine, manager, player_inputs, tick_rate=60)
)
```

### 3. Globální API

```python
from multipong.network.server import initialize_game_loop, get_game_loop

# Inicializace globální instance
loop = initialize_game_loop(engine, manager)

# Získání instance odkudkoliv
loop = get_game_loop()
```

## ⚙️ Konfigurace

### Tick Rate

V `config.json`:

```json
{
  "server_tick_rate": 60
}
```

Načteno v `settings.py`:

```python
from multipong import settings

tick_rate = settings.SERVER_TICK_RATE  # 60 Hz (default)
```

## 🔄 Game Loop Cyklus

Každý tick (např. každých 16.67ms při 60 Hz):

1. **Aktualizace enginu** - `engine.update(player_inputs)`
2. **Získání stavu** - `state = engine.get_state()`
3. **Příprava snapshotu** - `{"type": "snapshot", **state}`
4. **Broadcast** - `manager.broadcast(snapshot)`
5. **Čekání** - `await asyncio.sleep(tick_interval)`

## 📊 Logování

Game loop loguje:

```
INFO - 🎮 GameLoop inicializován (tick rate: 60 Hz)
INFO - 🚀 Game loop spuštěn (interval: 0.0167s)
DEBUG - 📊 Tick #60 | Hráči: 2 | Broadcast: 2 | Score: {'A': 0, 'B': 0}
WARNING - ⚠️ Tick #120 přesáhl interval: 0.0200s > 0.0167s
INFO - 🛑 Game loop byl zrušen (CancelledError)
INFO - 🏁 Game loop ukončen (celkem ticků: 120)
```

## 🧪 Testování

### Spuštění testů

```powershell
pytest tests/network/test_game_loop.py -v
```

**Výsledky:** 11/11 testů prošlo ✅

Testy pokrývají:
- ✅ Inicializaci s výchozím/vlastním tick rate
- ✅ Aktualizaci a vymazání vstupů
- ✅ Deep copy vstupů
- ✅ Běh loop s engine a managerem
- ✅ Zpracování vstupů během běhu
- ✅ Zastavení loop
- ✅ Globální API (initialize/get)
- ✅ Funkční API run_game_loop()

### Demo příklad

```powershell
python -m multipong.network.server.demo_game_loop
```

**Výstup:**
- Simuluje 2 hráče (A1, B1)
- Běží 2 sekundy s tick rate 30 Hz
- Zobrazuje broadcast count (~60 snapshots)
- Ukazuje poslední snapshot s pozicí míčku a score

## 💡 Příklady použití

### Integrace se serverem

```python
from fastapi import FastAPI, WebSocket
from multipong.engine import MultipongEngine
from multipong.network.server import (
    WebSocketManager,
    PlayerSession,
    GameLoop
)

app = FastAPI()
engine = MultipongEngine()
manager = WebSocketManager()
game_loop = GameLoop(engine, manager)

@app.on_event("startup")
async def startup():
    # Spuštění game loop při startu serveru
    asyncio.create_task(game_loop.run())

@app.websocket("/ws/{player_id}")
async def ws_endpoint(websocket: WebSocket, player_id: str):
    await websocket.accept()
    session = PlayerSession(websocket, player_id)
    await manager.add(session)
    
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "input":
                # Aktualizace vstupů v game loop
                game_loop.update_input(
                    player_id,
                    up=data["up"],
                    down=data["down"]
                )
    except:
        await manager.remove(session)
        game_loop.clear_input(player_id)
```

### Změna tick rate za běhu

```python
# Nový loop s jiným tick rate
slow_loop = GameLoop(engine, manager, tick_rate=30)
fast_loop = GameLoop(engine, manager, tick_rate=120)
```

### Monitorování performance

```python
loop = GameLoop(engine, manager)

# Před spuštěním
start_time = asyncio.get_event_loop().time()
task = asyncio.create_task(loop.run())

# Po nějaké době
await asyncio.sleep(10)
loop.stop()
await task

# Analýza
# Logování už obsahuje info o tickách a případných zpožděních
```

## 🔍 API Reference

### GameLoop

```python
class GameLoop:
    def __init__(
        self,
        engine: MultipongEngine,
        manager: WebSocketManager,
        tick_rate: int = None  # None = použije settings.SERVER_TICK_RATE
    )
    
    def update_input(self, player_id: str, up: bool, down: bool) -> None
    def clear_input(self, player_id: str) -> None
    def get_current_inputs(self) -> Dict[str, Dict[str, bool]]
    
    async def run(self) -> None
    def stop(self) -> None
    
    # Attributes
    engine: MultipongEngine
    manager: WebSocketManager
    tick_rate: int
    is_running: bool
    player_inputs: Dict[str, Dict[str, bool]]
```

### Funkční API

```python
async def run_game_loop(
    engine: MultipongEngine,
    manager: WebSocketManager,
    player_inputs: Dict[str, Dict[str, bool]],
    tick_rate: int = None
) -> None
```

### Globální API

```python
def initialize_game_loop(
    engine: MultipongEngine,
    manager: WebSocketManager,
    tick_rate: int = None
) -> GameLoop

def get_game_loop() -> GameLoop | None
```

## 📈 Performance

Při tick rate **60 Hz**:
- Interval: **16.67 ms**
- Snapshots za sekundu: **60**
- Teoretický overhead: **< 1 ms** per tick (engine update + broadcast)

Při **2 hráčích** za **1 sekundu**:
- Engine updates: **60×**
- Broadcasts: **120** (60× pro každého hráče)

## ⚠️ Poznámky

1. **Tick rate** - Výchozí 60 Hz, konfigurovatelné
2. **Input sharing** - `player_inputs` je sdílená mapa, změny se okamžitě projeví
3. **Deep copy** - `get_current_inputs()` vrací deep copy kvůli bezpečnosti
4. **Graceful shutdown** - `stop()` nastaví flag, loop se ukončí na dalším ticku
5. **Error handling** - Výjimky v loop jsou logovány a propagovány

## 🚀 Další kroky (Phase 4)

Co zbývá:
- ⏳ Integrace game loop do `websocket_server.py`
- ⏳ Lobby systém pro automatické přidělování slotů
- ⏳ Heartbeat/ping-pong pro keep-alive
- ⏳ Reconnect logika
- ⏳ Metriky a monitoring (tick timing, lag detection)

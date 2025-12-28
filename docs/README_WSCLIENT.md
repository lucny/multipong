# 🎮 WSClient - MULTIPONG WebSocket Client

Asynchronní WebSocket klient pro připojení k MULTIPONG serveru (Phase 5).

---

## 🚀 Rychlý start

### Instalace
```bash
pip install websockets
```

### Základní použití
```python
import asyncio
from multipong.network.client import WSClient, StateBuffer

async def main():
    # Buffer pro snapshoty
    buffer = StateBuffer()
    
    # Vytvoření klienta
    client = WSClient(
        url="ws://localhost:8000/ws",
        player_id="auto",  # nebo "A1", "B2" atd.
        on_snapshot=buffer.add_state
    )
    
    # Připojení
    await client.connect()
    
    # Herní smyčka
    while client.is_connected():
        # Získej interpolovaný stav
        state = buffer.get_interpolated()
        
        # Odešli vstupy
        await client.send_input(up=True, down=False)
        
        # Vyrenderuj stav
        if state:
            print(f"Ball: {state['ball']['x']:.1f}, {state['ball']['y']:.1f}")
        
        await asyncio.sleep(1/60)
    
    await client.disconnect()

asyncio.run(main())
```

---

## ✨ Funkce

### WSClient
- ✅ Asynchronní připojení k serveru
- ✅ Automatické přidělení pozice (`player_id="auto"`)
- ✅ Posílání vstupů (up/down)
- ✅ Chat zprávy
- ✅ Ping/pong keep-alive
- ✅ Callback systém pro různé události

### StateBuffer
- ✅ Ukládání posledních 3 snapshotů
- ✅ Interpolace pro plynulý rendering
- ✅ Automatické timestamping
- ✅ Konfigurovatelná velikost bufferu

---

## 📡 Demo aplikace

```bash
# Automatické přidělení pozice
python -m multipong.network.client.demo_ws_client

# Konkrétní pozice
python -m multipong.network.client.demo_ws_client A1

# Vlastní server
python -m multipong.network.client.demo_ws_client auto ws://192.168.1.100:8000/ws
```

**Výstup:**
```
🚀 MULTIPONG Demo WebSocket Client
   Server: ws://localhost:8000/ws
   Player ID: auto

✅ Připojeno k serveru, čekám na zprávy...
🎮 Přidělena pozice: A1
   Lobby: 1/6 hráčů

💓 Ping odeslán
📊 Přijato 30 snapshotů
   Míček: x=620.5, y=430.2

📈 Status:
   Přijato snapshotů: 60
   Buffer: 3 snapshotů
   Klient: WSClient(player_id=auto, slot=A1, status=connected)
```

---

## 🧪 Testování

```bash
# Unit testy (21 testů)
pytest tests/network/test_ws_client.py -v

# S code coverage
pytest tests/network/test_ws_client.py --cov=multipong.network.client

# Všechny network testy
pytest tests/network/ -v
```

**Výsledky:**
- ✅ 21/21 testů prošlo
- ✅ WSClient: 50% coverage
- ✅ StateBuffer: 73% coverage

---

## 📖 API Reference

### WSClient

#### Constructor
```python
WSClient(
    url: str,
    player_id: str,
    on_snapshot: Optional[Callable[[dict], None]] = None,
    on_connected: Optional[Callable[[dict], None]] = None,
    on_chat: Optional[Callable[[str, str], None]] = None
)
```

#### Metody
- `async connect() -> bool` - Připojení k serveru
- `async send_input(up: bool, down: bool)` - Odeslání vstupů
- `async send_chat(message: str)` - Odeslání chat zprávy
- `async send_ping()` - Odeslání ping zprávy
- `async disconnect()` - Odpojení od serveru
- `is_connected() -> bool` - Kontrola spojení
- `get_assigned_slot() -> Optional[str]` - Vrátí přidělenou pozici

---

### StateBuffer

#### Constructor
```python
StateBuffer(max_size: int = 3)
```

#### Metody
- `add_state(state: dict)` - Přidá snapshot s timestampem
- `get_latest() -> Optional[dict]` - Vrátí poslední snapshot
- `get_interpolated(render_delay: float = 0.0) -> Optional[dict]` - Vrátí interpolovaný stav
- `clear()` - Vyčistí buffer
- `size() -> int` - Vrátí počet snapshotů

---

## 🎯 Příklady

### Callback funkce
```python
def on_snapshot(data):
    print(f"Snapshot přijat: ball={data['ball']}")

def on_connected(data):
    print(f"Připojeno jako {data['assigned_slot']}")

def on_chat(sender, message):
    print(f"[{sender}]: {message}")

client = WSClient(
    "ws://localhost:8000/ws",
    "auto",
    on_snapshot=on_snapshot,
    on_connected=on_connected,
    on_chat=on_chat
)
```

### Chat komunikace
```python
# Odeslání chat zprávy
await client.send_chat("Hello everyone!")

# Callback při příjmu
def on_chat(sender, message):
    if message.startswith("/"):
        # Zpracuj command
        pass
    else:
        print(f"{sender}: {message}")
```

### Keep-alive ping
```python
# Ping každých 5 sekund
async def ping_loop(client):
    while client.is_connected():
        await client.send_ping()
        await asyncio.sleep(5)

asyncio.create_task(ping_loop(client))
```

### Interpolace s custom delay
```python
# Render delay 50ms pro kompenzaci latence
state = buffer.get_interpolated(render_delay=0.05)
```

---

## 🔧 Protokol zpráv

### Klient → Server
```json
// Input
{"type": "input", "up": true, "down": false}

// Chat
{"type": "chat", "message": "Hello!"}

// Ping
{"type": "ping"}
```

### Server → Klient
```json
// Connected (při připojení)
{
  "type": "connected",
  "assigned_slot": "A1",
  "lobby_status": {...}
}

// Snapshot (game state)
{
  "type": "snapshot",
  "ball": {"x": 620, "y": 430, "radius": 10},
  "team_left": {...},
  "team_right": {...}
}

// Chat
{
  "type": "chat",
  "player_id": "A1",
  "message": "GG!"
}

// Pong
{"type": "pong"}
```

---

## 🐛 Troubleshooting

### Klient se nemůže připojit
```python
# Zkontroluj, že server běží
# Zkontroluj URL a port
client = WSClient("ws://localhost:8000/ws", "auto")
connected = await client.connect()
if not connected:
    print("Server není dostupný")
```

### Není přidělena pozice
```python
# Server vrátil error (lobby plné)
def on_connected(data):
    if "error" in data:
        print(f"Error: {data['message']}")
    else:
        print(f"Slot: {data['assigned_slot']}")
```

### Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# WSClient loguje:
# - DEBUG: Detailní komunikace
# - INFO: Připojení, pozice, chat
# - ERROR: Chyby
```

---

## 📚 Viz také

- [PHASE5_CLIENT.md](PHASE5_CLIENT.md) - Kompletní dokumentace
- [06_phase5_client_sync.md](06_phase5_client_sync.md) - Původní specifikace
- [Demo server](../multipong/network/server/) - Pro testování klienta

---

*Verze: 0.5.0 | Phase 5*

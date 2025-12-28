# 🎮 MULTIPONG Phase 5 - WebSocket Client Implementation

Implementace asynchronního WebSocket klienta pro připojení k MULTIPONG serveru.

---

## ✨ Implementované komponenty

### 📡 WSClient - WebSocket klient
Asynchronní klient pro komunikaci se serverem.

**Funkce:**
- ✅ Připojení k `ws://localhost:8000/ws/{player_id}`
- ✅ Asynchronní poslouchání snapshot zpráv
- ✅ Posílání input zpráv (up/down)
- ✅ Chat zprávy
- ✅ Ping/pong keep-alive
- ✅ Callback systém pro různé typy zpráv

**API:**
```python
from multipong.network.client import WSClient

# Vytvoření klienta s callback funkcemi
client = WSClient(
    url="ws://localhost:8000/ws",
    player_id="auto",  # nebo "A1", "B2" atd.
    on_snapshot=lambda data: print(f"Snapshot: {data}"),
    on_connected=lambda data: print(f"Connected: {data}"),
    on_chat=lambda sender, msg: print(f"{sender}: {msg}")
)

# Připojení
await client.connect()

# Posílání vstupů
await client.send_input(up=True, down=False)

# Chat
await client.send_chat("Hello!")

# Ping
await client.send_ping()

# Odpojení
await client.disconnect()
```

---

### 🎯 StateBuffer - Interpolace snapshotů
Buffer pro ukládání a interpolaci game state.

**Funkce:**
- ✅ Ukládání posledních 3 snapshotů
- ✅ Interpolace mezi snapshoty pro plynulý rendering
- ✅ Automatické timestamping
- ✅ Konfigurovatelná velikost bufferu

**API:**
```python
from multipong.network.client import StateBuffer

# Vytvoření bufferu
buffer = StateBuffer(max_size=3)

# Přidání snapshot (automaticky timestampne)
buffer.add_state(snapshot_data)

# Získání posledního snapshotu
latest = buffer.get_latest()

# Získání interpolovaného stavu
interpolated = buffer.get_interpolated(render_delay=0.0)

# Interpolovaný stav obsahuje:
# - ball: interpolovaná pozice míčku
# - team_left/team_right: interpolované pozice pálek
# - goal_left/goal_right: goal zóny (nekopíruje se)
```

---

## 🧪 Demo aplikace

### Konzolový klient
```bash
# Automatické přidělení pozice
python -m multipong.network.client.demo_ws_client

# Konkrétní pozice
python -m multipong.network.client.demo_ws_client A1

# Vlastní server
python -m multipong.network.client.demo_ws_client auto ws://192.168.1.100:8000/ws
```

**Funkce demo klienta:**
- Připojení k serveru
- Automatické posílání vstupů (střídavě nahoru/dolů)
- Ping každých 5 sekund
- Logování přijatých zpráv
- Zobrazení statistik každých 10 sekund

---

## 📊 Protokol zpráv

### Klient → Server

#### Input zpráva
```json
{
  "type": "input",
  "up": true,
  "down": false
}
```

#### Chat zpráva
```json
{
  "type": "chat",
  "message": "Hello everyone!"
}
```

#### Ping zpráva
```json
{
  "type": "ping"
}
```

---

### Server → Klient

#### Connected zpráva (při připojení)
```json
{
  "type": "connected",
  "assigned_slot": "A1",
  "lobby_status": {
    "available": ["A3", "A4"],
    "occupied": {"A1": "A1", "B1": "B1"},
    "total_slots": 6,
    "players_count": 2
  }
}
```

#### Snapshot zpráva (game state)
```json
{
  "type": "snapshot",
  "ball": {
    "x": 620,
    "y": 430,
    "radius": 10,
    "vx": 5.2,
    "vy": -3.1
  },
  "team_left": {
    "name": "Left Team",
    "score": 2,
    "paddles": [
      {
        "player_id": "A1",
        "x": 10,
        "y": 350,
        "width": 10,
        "height": 50,
        "hits": 15,
        "goals_scored": 1,
        "goals_received": 0
      }
    ]
  },
  "team_right": { /* ... */ },
  "goal_left": {"top": 300, "bottom": 500},
  "goal_right": {"top": 300, "bottom": 500}
}
```

#### Chat zpráva (broadcast)
```json
{
  "type": "chat",
  "player_id": "A1",
  "message": "Good game!"
}
```

#### Pong zpráva
```json
{
  "type": "pong"
}
```

---

## 🧮 Interpolace

StateBuffer automaticky interpoluje mezi dvěma posledními snapshoty:

```
Snapshot 1 (t=0.00s):  ball.x = 100
Snapshot 2 (t=0.05s):  ball.x = 150

Interpolace (t=0.025s, alpha=0.5):
  ball.x = 100 * (1 - 0.5) + 150 * 0.5 = 125
```

**Výhody:**
- Plynulý pohyb i při 20-30 Hz network update
- Kompenzace síťové latence
- Rendering může běžet na 60 FPS nezávisle

**Interpolované objekty:**
- ✅ Míček (x, y)
- ✅ Pálky (x, y)
- ❌ Skóre (kopíruje se z nejnovějšího)
- ❌ Goal zóny (kopíruje se)

---

## 🧪 Testování

### Unit testy
```bash
# WSClient a StateBuffer testy (21 testů)
pytest tests/network/test_ws_client.py -v

# Všechny network testy
pytest tests/network/ -v
```

**Výsledky:**
- ✅ 21/21 testů prošlo (100%)
- ✅ WSClient: 50% coverage (async funkce těžko testovatelné bez živého serveru)
- ✅ StateBuffer: 73% coverage

### Integrační test

1. **Spusť server:**
   ```bash
   python -m multipong.network.server.websocket_server
   ```

2. **Spusť demo klienta:**
   ```bash
   python -m multipong.network.client.demo_ws_client
   ```

3. **Očekávaný výstup:**
   ```
   ✅ Připojeno k serveru jako auto
   🎮 Přidělena pozice: A1
   💓 Ping odeslán
   📊 Přijato 30 snapshotů
      Míček: x=620.5, y=430.2
   ```

---

## 📁 Struktura souborů

```
multipong/network/client/
├── __init__.py              # ✨ Exporty WSClient, StateBuffer
├── ws_client.py             # 🆕 Asynchronní WebSocket klient
├── state_buffer.py          # 🆕 Buffer + interpolace
├── demo_ws_client.py        # 🆕 Demo konzolová aplikace
├── client.py                # (starý klient - deprecated)
└── client_main.py           # (starý main - deprecated)

tests/network/
└── test_ws_client.py        # 🆕 21 unit testů
```

---

## 🔧 Konfigurace

### Požadované balíčky
```bash
pip install websockets  # Pro async WebSocket komunikaci
```

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)

# WSClient automaticky loguje:
# - INFO: Připojení, odpojení, přidělená pozice
# - DEBUG: Ping/pong, detailní vstupy
# - ERROR: Chyby při komunikaci
```

---

## 🎯 Příklady použití

### Jednoduchý klient
```python
import asyncio
from multipong.network.client import WSClient, StateBuffer

async def main():
    buffer = StateBuffer()
    
    client = WSClient(
        url="ws://localhost:8000/ws",
        player_id="A1",
        on_snapshot=buffer.add_state
    )
    
    await client.connect()
    
    # Herní smyčka
    while client.is_connected():
        # Získej interpolovaný stav
        state = buffer.get_interpolated()
        
        # Zpracuj vstupy (např. z Pygame)
        up = check_key_up()
        down = check_key_down()
        await client.send_input(up, down)
        
        # Vyrenderuj stav
        if state:
            render(state)
        
        await asyncio.sleep(1/60)  # 60 FPS
    
    await client.disconnect()

asyncio.run(main())
```

### S Pygame renderem
```python
import asyncio
import pygame
from multipong.network.client import WSClient, StateBuffer

async def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    
    buffer = StateBuffer()
    client = WSClient("ws://localhost:8000/ws", "auto", buffer.add_state)
    
    await client.connect()
    
    running = True
    while running and client.is_connected():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Vstupy
        keys = pygame.key.get_pressed()
        await client.send_input(
            up=keys[pygame.K_UP],
            down=keys[pygame.K_DOWN]
        )
        
        # Rendering
        state = buffer.get_interpolated()
        if state:
            screen.fill((0, 0, 0))
            
            # Míček
            ball = state["ball"]
            pygame.draw.circle(screen, (255, 255, 255),
                             (int(ball["x"]), int(ball["y"])),
                             ball["radius"])
            
            # Pálky
            for team in ["team_left", "team_right"]:
                for paddle in state[team]["paddles"]:
                    pygame.draw.rect(screen, (200, 200, 200),
                                   (paddle["x"], paddle["y"],
                                    paddle["width"], paddle["height"]))
            
            pygame.display.flip()
        
        clock.tick(60)
    
    await client.disconnect()
    pygame.quit()

asyncio.run(game_loop())
```

---

## 🚀 Další kroky

Pro kompletní Phase 5 zbývá:
1. ✅ WSClient - hotovo
2. ✅ StateBuffer - hotovo
3. ⏳ Pygame renderer (UI/renderer.py)
4. ⏳ Hlavní klientská aplikace (main_client.py)
5. ⏳ Úprava serveru - posílat pozice pálek v snapshotu

---

## 📊 Výsledky implementace

| Komponenta | Status | Popis |
|------------|--------|-------|
| WSClient | ✅ Hotovo | Async WebSocket klient s callback systémem |
| StateBuffer | ✅ Hotovo | Buffer + interpolace snapshotů |
| Demo klient | ✅ Hotovo | Konzolová aplikace pro testování |
| Unit testy | ✅ Hotovo | 21 testů, 100% pass rate |
| Dokumentace | ✅ Hotovo | API + příklady + protokol |

---

*Vytvořeno: 25. listopadu 2025*  
*Verze: 0.5.0*  
*Phase: 5 (Client Sync)*

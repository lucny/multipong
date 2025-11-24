# **06_phase5_client_sync.md — Pygame klient, synchronizace a komunikace se serverem**

## 🎯 1. Cíle fáze 5

V této fázi vytvoříme plně funkční **síťový herní klient**, který:

* se připojí k WebSocket serveru
* odešle identifikaci hráče (např. „A1“)
* **odesílá vstupy** (up/down)
* **přijímá snapshoty stavu hry**
* vykresluje herní scénu podle dat ze serveru
* používá **interpolaci**, aby byl pohyb plynulý i při 20–30 Hz síťových updatech

Tím vzniká první použitelná síťová verze MULTIPONG.

---

# 🧠 2. Proč potřebujeme klientskou synchronizaci?

Protože:

* server rozhoduje o veškeré fyzice hry
* klient pouze vykresluje a zachycuje vstupy
* síť má latenci (typicky 10–50 ms)
* snapshoty chodí méně často než render loop (např. 30× vs. 60 FPS)

Proto potřebujeme:

* **buffer snapshotů**
* **interpolaci mezi snapshoty**
* oddělení logiky renderu od logiky networkingu

---

# 🧱 3. Struktura klientského modulu

Vytvoříme nové soubory:

```
multipong/
│
├── multipong/
│     ├── network/
│     │     └── client/
│     │           ├── ws_client.py
│     │           ├── state_buffer.py
│     │           └── message_decoder.py
│     ├── ui/
│     │     └── renderer.py
│     └── main_client.py
│
└── docs/
      └── 06_phase5_client_sync.md
```

---

# 🟦 4. WebSocket klient – `ws_client.py`

Použijeme knihovnu **websockets** (asynchronní).

Instalace:

```
pip install websockets
```

`soubor: multipong/network/client/ws_client.py`

```python
import asyncio
import json
import websockets

class WSClient:
    """
    Asynchronní klient pro komunikaci se serverem MULTIPONG.
    Odesílá vstupy a přijímá snapshoty.
    """

    def __init__(self, url, player_id, on_snapshot):
        self.url = url
        self.player_id = player_id
        self.on_snapshot = on_snapshot   # callback při příjmu snapshotu
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(f"{self.url}/{self.player_id}")
        asyncio.create_task(self._listen())

    async def _listen(self):
        """Přijímá zprávy od serveru."""
        try:
            while True:
                msg = await self.ws.recv()
                data = json.loads(msg)

                if data["type"] == "snapshot":
                    self.on_snapshot(data)
        except:
            print("Disconnected from server.")

    async def send_input(self, up, down):
        """Odesílá vstupy hráče serveru."""
        if self.ws:
            msg = {
                "type": "input",
                "player_id": self.player_id,
                "up": up,
                "down": down
            }
            await self.ws.send(json.dumps(msg))
```

---

# 🟫 5. Buffer snapshotů – `state_buffer.py`

Aby byl pohyb plynulý, potřebujeme ukládat dva poslední snapshoty a interpolovat mezi nimi.

`soubor: multipong/network/client/state_buffer.py`

```python
import time

class StateBuffer:
    """
    Uchovává několik posledních snapshotů.
    Klient renderuje interpolovaný stav mezi nimi.
    """

    def __init__(self):
        self.buffer = []  # list of (timestamp, state)

    def add_state(self, state):
        ts = time.time()
        self.buffer.append((ts, state))

        # držíme pouze poslední 3 snapshoty
        if len(self.buffer) > 3:
            self.buffer.pop(0)

    def get_interpolated(self):
        """
        Vrátí interpolovaný stav mezi dvěma posledními snapshoty.
        Pokud to nejde, vrací poslední stav.
        """

        if len(self.buffer) < 2:
            return self.buffer[-1][1] if self.buffer else None

        (t1, s1), (t2, s2) = self.buffer[-2], self.buffer[-1]

        now = time.time()
        alpha = min(1.0, max(0.0, (now - t2) / (t2 - t1)))

        interp = {}

        # interpolace objektů (míček + pálky)
        interp["ball"] = {
            "x": s1["ball"]["x"] * (1 - alpha) + s2["ball"]["x"] * alpha,
            "y": s1["ball"]["y"] * (1 - alpha) + s2["ball"]["y"] * alpha,
            "radius": s2["ball"]["radius"]
        }

        # týmy kopírujeme zatím bez interpolace
        interp["team_left"] = s2["team_left"]
        interp["team_right"] = s2["team_right"]
        interp["goal_left"] = s2["goal_left"]
        interp["goal_right"] = s2["goal_right"]

        return interp
```

---

# 🎨 6. Renderer – `renderer.py`

Z UI nyní odstraníme logiku hry – pouze vykresluje snapshot.

`soubor: multipong/ui/renderer.py`

```python
import pygame
from settings import COLOR_BACKGROUND, COLOR_PADDLE

class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw(self, state):
        self.screen.fill(COLOR_BACKGROUND)

        # míček
        ball = state["ball"]
        pygame.draw.circle(self.screen, (200, 80, 80),
                           (int(ball["x"]), int(ball["y"])),
                           ball["radius"])

        # všechny pálky
        for team_key in ["team_left", "team_right"]:
            team = state[team_key]
            for pstat in team["paddles"]:
                # engine zatím vrátil jen statistiky — doplníme pozici
                # (o tu se musí postarat server – bude doplněno v další fázi)
                pass

        pygame.display.flip()
```

> POZNÁMKA:
> Ve fázi 3 server zatím neobsahuje pozice pálek v `Team.to_dict()`, jen statistiky.
> Ve fázi 6 to doplníme (viz níže v tomto dokumentu).

---

# 🎮 7. Klientská aplikace – `main_client.py`

`soubor: multipong/main_client.py`

```python
import asyncio
import pygame

from network.client.ws_client import WSClient
from network.client.state_buffer import StateBuffer
from ui.renderer import Renderer
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("MULTIPONG Client")

    buffer = StateBuffer()
    renderer = Renderer(screen)

    # nastav hráče, např. A1
    player_id = "A1"
    client = WSClient("ws://localhost:8000/ws", player_id, buffer.add_state)
    await client.connect()

    clock = pygame.time.Clock()
    running = True

    while running:
        up = down = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        up = keys[pygame.K_UP]
        down = keys[pygame.K_DOWN]

        # odešli vstupy
        await client.send_input(up, down)

        # získej interpolovaný stav
        state = buffer.get_interpolated()
        if state:
            renderer.draw(state)

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
```

---

# 🧩 8. Důležitá úprava: server musí posílat i pozice pálek

V dokumentu z fáze 3 posílal server jen statistiky týmů.
Nyní musíme upravit `Team.to_dict()` takto:

```python
def to_dict(self):
    return {
        "name": self.name,
        "score": self.score,
        "paddles": [
            {
                "player_id": p.stats.player_id,
                "x": p.x,
                "y": p.y,
                "width": p.width,
                "height": p.height,
                "hits": p.stats.hits,
                "goals_scored": p.stats.goals_scored,
                "goals_received": p.stats.goals_received
            }
            for p in self.paddles
        ]
    }
```

Díky tomu renderer získá přesné pozice.

---

# 🎨 9. Doplnění do rendereru

Vrátime se do `renderer.draw()`:

```python
for team_key in ["team_left", "team_right"]:
    team = state[team_key]
    for p in team["paddles"]:
        pygame.draw.rect(
            self.screen,
            COLOR_PADDLE,
            (p["x"], p["y"], p["width"], p["height"])
        )
```

---

# 🧪 10. Test klienta

Spusť server:

```
uvicorn multipong.network.server.websocket_server:app --reload
```

V jiném terminálu spusť klienta:

```
python multipong/main_client.py
```

Pokud server běží a posílá snapshoty:

✔ uvidíš míček i pálku A1 (tvou control)
✔ zbytek pálek stojí (dokud nedoplníme AI nebo ostatní hráče)

---

# 🧪 11. Mini výzvy pro studenty

### 🔹 1) Přidej možnost výběru hráče při startu

Prompt pro Copilot:

> „Přidej do Pygame klienta textový input, kde hráč zadá svoje player_id.“

### 🔹 2) Přidej jednoduchý smoothing

Změkčování pozice míčku i pálek pomocí lerp funkce v rendereru.

### 🔹 3) Upozornění při ztrátě spojení

Klient zobrazí zprávu „Disconnected“.

### 🔹 4) Přidej základní systém latency metričky

`ping` mezi klientem a serverem.

---


# **13_phase12_menu_and_lobby.md — Úvodní menu, volba hráče, týmy a lobby systém**

## 🎯 1. Cíle fáze 12

V této fázi vytvoříme robustní **uživatelské rozhraní před samotným zápasem**, tzv. **lobby**:

* úvodní menu (Start Game, Multiplayer, Settings, Quit)
* lokální volba hráčského režimu (1P / 2P / AI)
* připojení k multiplayer serveru
* výběr týmu (A nebo B)
* přiřazení pálky / hráčského slotu
* synchronizaci lobby mezi klienty
* start zápasu teprve ve chvíli, kdy jsou týmy připravené
* fallback pravidla (neobsazené pálky doplní AI)

Lobby je klíčové pro reálné hraní — umožní **organizaci zápasů**, přidání nových hráčů, zobrazení seznamu připojených klientů, zvolení obtížnosti AI a nastavení zápasu.

---

# 🧠 2. Co je to „lobby“?

Lobby je místnost (stav serveru), kde:

* hráči se připojí přes WebSocket
* vyberou si tým (A / B)
* vyberou si pozici (A1, A2…)
* vidí ostatní hráče online
* čekají, než všichni potvrdí „Ready“

Server pak:

* vytvoří instanci `MultipongEngine`
* rozdělí hráče mezi pálky
* spustí countdown
* spustí zápas

---

# 🔄 3. Stav lobby na serveru

Lobby server bude mít vlastní datovou strukturu:

```
LobbyState:
  players:
    A1: { id: "Pepa",  status: "ready" }
    A2: { id: "AI",    status: "ai" }
    B1: { id: "Katka", status: "ready" }
    B2: { id: null,    status: "free" }

  settings:
    match_duration: 180
    goal_size: 200
    paddle_speed: 6
```

### Stav hráče může být:

* `"free"`
* `"human"`
* `"ai"`
* `"ready"`

---

# 🟦 4. Rozšíření WebSocket protokolu o lobby zprávy

Každý klient může poslat:

### 4.1 Po připojení

```json
{
  "type": "join_lobby",
  "player_name": "Pepa"
}
```

### 4.2 Žádost o obsazení pozice (např. A2)

```json
{
  "type": "choose_slot",
  "slot": "A2"
}
```

### 4.3 Přepnutí na „ready“

```json
{
  "type": "set_ready",
  "ready": true
}
```

### 4.4 Změna AI obtížnosti

```json
{
  "type": "set_ai_level",
  "slot": "B4",
  "level": "predictive"
}
```

---

# 🟥 5. Server: `LobbyManager`

Vytvoříme nový modul:

`soubor: multipong/network/server/lobby.py`

```python
class LobbyManager:
    def __init__(self):
        self.slots = {
            "A1": None, "A2": None, "A3": None, "A4": None,
            "B1": None, "B2": None, "B3": None, "B4": None
        }
        self.ready = set()
        self.settings = {
            "match_duration": 180,
            "goal_size": 200
        }

    def assign_slot(self, slot, player_name):
        if self.slots[slot] is None:
            self.slots[slot] = player_name
            return True
        return False

    def free_slot(self, slot):
        self.slots[slot] = None

    def set_ready(self, player_name, is_ready):
        if is_ready:
            self.ready.add(player_name)
        else:
            self.ready.discard(player_name)

    def all_ready(self):
        # volné sloty = automaticky AI
        used_slots = [s for s,p in self.slots.items() if p is not None]
        return len(self.ready) == len(used_slots)

    def get_state(self):
        return {
            "slots": self.slots,
            "ready_players": list(self.ready),
            "settings": self.settings
        }
```

---

# 🟧 6. WebSocket server – lobby logika

Doplníme do `websocket_server.py`:

```python
from .lobby import LobbyManager

lobby = LobbyManager()
```

A pak v `_listen()` zpracujeme nové typy zpráv:

### 6.1 Zapojení klienta do lobby

```python
elif msg["type"] == "join_lobby":
    session.player_name = msg["player_name"]
    # broadcasting aktualizovaného lobby stavu
    await manager.broadcast({
        "type": "lobby_update",
        **lobby.get_state()
    })
```

### 6.2 Obsazení slotu

```python
elif msg["type"] == "choose_slot":
    if lobby.assign_slot(msg["slot"], session.player_name):
        await manager.broadcast({
            "type": "lobby_update",
            **lobby.get_state()
        })
```

### 6.3 Nastavení ready

```python
elif msg["type"] == "set_ready":
    lobby.set_ready(session.player_name, msg["ready"])
    await manager.broadcast({
        "type": "lobby_update",
        **lobby.get_state()
    })

    if lobby.all_ready():
        # spustíme hru
        await start_match()
```

---

# 🟩 7. Start zápasu z lobby

Když všichni hráči jsou ready → server odešle:

```json
{
  "type": "start_match",
  "countdown": 3
}
```

Klienti si zobrazí 3–2–1 → Start.

Pak server:

* vytvoří `MultipongEngine`
* podle obsazených slotů nastaví lidské hráče a AI
* spustí tick loop

---

# 🎨 8. Pygame klient: grafické lobby

Vytvoříme stav `STATE_LOBBY` v klientovi:

```
STATE_MENU → STATE_LOBBY → STATE_GAME → STATE_RESULTS
```

## 8.1 Zobrazení slotů

Příklad rozložení:

```
Tým A                          Tým B
 A1: [ prázdné ]               B1: [ Katka ]
 A2: [ Pepa ]                  B2: [ AI ]
 A3: [ prázdné ]               B3: [ prázdné ]
 A4: [ prázdné ]               B4: [ prázdné ]
```

Studenti si mohou vytvořit klikatelné boxy.

---

# 🔄 9. Synchronizace lobby u klientů

Klient přijímá:

```json
{
  "type": "lobby_update",
  "slots": {...},
  "ready_players": [...],
  "settings": {...}
}
```

A aktualizuje objekt `LobbyState` na straně klienta.

---

# 🏁 10. Start hry – přepnutí stavu

Když klient dostane:

```json
{ "type": "start_match", "countdown": 3 }
```

→ zobrazí countdown (text 3, 2, 1)
→ přepne do `STATE_GAME`
→ začne herní render a síťová komunikace (Phase 5).

---

# 🧪 11. Mini úkoly pro studenty

### 🔹 1) Přidej do lobby chat

Jednoduché zprávy formou:

```json
{ "type": "chat", "from": "Pepa", "text": "Ahoj!" }
```

### 🔹 2) Obarvi obsazené sloty podle týmu

Modrá = tým A
Červená = tým B

### 🔹 3) Vytvoř „AI preview“

Když slot je AI → zobraz jméno a typ (Simple / Predictive / Q-learning).

### 🔹 4) Copilot prompt

> „Vytvoř klikací menu v Pygame, které umožní hráči vybrat slot (A1–A4, B1–B4) a označit se jako ready.“



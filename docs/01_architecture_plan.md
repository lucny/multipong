# **01_architecture_plan.md — Architektonický plán projektu MULTIPONG**

## 🎮 1. Účel dokumentu

Tento dokument definuje **celkovou architekturu projektu MULTIPONG**.
Slouží jako:

* výukový materiál pro studenty
* plán pro týmový vývoj
* referenční základna pro Copilot Pro
* dokumentace technického řešení

Obsahuje přehled hlavních modulů, návrhové principy, komunikaci mezi komponentami a technické standardy projektu.

---

# 🏗 2. Vysoká úroveň architektury

MULTIPONG bude kombinovat několik technologických vrstev:

```
+----------------------------------------------------+
|                  FRONTEND LAYER                    |
|   Web UI, Mobile App (Flutter), Scoreboard         |
+----------------------------------------------------+

+----------------------------------------------------+
|                    REST API LAYER                  |
|                   (FastAPI, JSON)                  |
|            /players /matches /leaderboard          |
+----------------------------------------------------+

+----------------------------------------------------+
|                REALTIME GAME LAYER                 |
|              (FastAPI WebSockets, asyncio)         |
|  - Multiplayer server                              |
|  - Tick loop (game physics, collisions, scoring)   |
|  - Synchronization with clients                    |
+----------------------------------------------------+

+----------------------------------------------------+
|                    GAME ENGINE                      |
|              (OOP: Pygame-agnostic logic)           |
|   - Game state                                      |
|   - Teams, paddles, ball                            |
|   - Rules, collisions, match control                |
+----------------------------------------------------+

+----------------------------------------------------+
|                PRESENTATION LAYER                   |
|                  (Pygame client)                    |
|   - Rendering                                       |
|   - Input capture                                   |
|   - Sync with server snapshots                      |
+----------------------------------------------------+

+----------------------------------------------------+
|                  DATABASE LAYER                     |
|            (SQLite / PostgreSQL + SQLAlchemy)       |
|   - Player data                                     |
|   - Match results                                   |
|   - Statistics                                      |
+----------------------------------------------------+
```

---

# 🔧 3. Hlavní části projektu

## 3.1 Game Engine (čisté OOP, bez Pygame)

Engine je **jádro logiky hry**, nezávislé na síti a grafice.

### Obsahuje třídy:

* `GameState`
* `Ball`
* `Paddle`
* `Team`
* `Arena`
* `MatchController`
* `CollisionDetector`

### Engine:

* počítá fyziku (pohyb míčku)
* zpracovává kolize
* zaznamenává skóre
* eviduje zásahy
* řídí trvání zápasu
* vytváří stavový snapshot (dict) → posílaný klientům

### Klíčové pravidlo:

**Engine nesmí obsahovat žádné Pygame volání.**

---

## 3.2 Realtime server (WebSockety + asyncio)

Server:

* běží hlavní tick smyčku (např. 30–120 Hz)
* spravuje připojené hráče
* registruje inputy
* aktualizuje engine
* rozesílá stavy klientům

### Klíčové komponenty:

* `WebSocketManager`
* `PlayerSession`
* `LobbyHandler`
* `GameLoopController`
* `InputProcessor`

### Princip komunikace:

**Klient → Server:**

```json
{
  "type": "input",
  "player_id": 7,
  "move": "UP"
}
```

**Server → Klient:**

```json
{
  "type": "snapshot",
  "ball": { "x": 510, "y": 390 },
  "paddles": [...],
  "score": { "A": 3, "B": 2 },
  "time_left": 41
}
```

---

## 3.3 Pygame klient (front-end hry)

Klient:

* přijímá snapshoty od serveru
* interpoluje pohyb (smooth rendering)
* zachytává vstupy hráče (UP/DOWN)
* odesílá je serveru
* vykresluje scénu přes Pygame

### Vrstvy:

* `NetworkClient`
* `Renderer` (Pygame)
* `InputHandler`
* `ClientState` (místní kopie snapshotu)
* `InterpolationEngine`

### Klíčové pravidlo:

**Klient nikdy nepočítá herní logiku — to dělá server.**

---

## 3.4 REST API vrstva (FastAPI)

Zajišťuje přístup k uloženým datům:

* seznam hráčů
* historie zápasů
* globální leaderboard
* statistiky jednotlivých hráčů

### Příklady endpointů:

```
GET /players/
GET /players/{id}
GET /leaderboard/
POST /matches/
```

Datová vrstva komunikuje pomocí SQLAlchemy.

---

## 3.5 Databázová vrstva

Použije se:

* SQLite (lokálně ve škole)
* nebo PostgreSQL (pokročilejší nastavení)

### Tabulky:

* `players`
* `matches`
* `teams`
* `player_stats`
* `goals`
* `hits`
* `settings`

---

## 3.6 Budoucí externí frontendy

### Webový panel:

* zobrazuje výsledky
* grafy (např. Chart.js)
* detail hráčových zápasů

### Mobilní klient:

* Flutter / React Native
* připojení přes REST API

---

# 🧩 4. Návrh adresářové struktury (detailní)

```
multipong/
│
├── docs/
│     ├── 00_overview.md
│     ├── 01_architecture_plan.md
│     ├── ...
│
├── multipong/
│     ├── main.py                # klient
│     ├── settings.py
│     ├── config/
│     │     ├── config.json
│     │     └── config_loader.py
│     │
│     ├── engine/                # čistý game engine
│     │     ├── ball.py
│     │     ├── paddle.py
│     │     ├── team.py
│     │     ├── arena.py
│     │     ├── gamestate.py
│     │     ├── match_controller.py
│
│     ├── network/
│     │     ├── server/
│     │     │     ├── websocket_server.py
│     │     │     ├── game_loop.py
│     │     │     ├── player_session.py
│     │     │     └── protocol.py
│     │     ├── client/
│     │     │     ├── ws_client.py
│     │     │     └── message_decoder.py
│     │
│     ├── ui/
│     │     ├── renderer.py
│     │     ├── sprites/
│     │     └── fonts/
│     │
│     ├── data/
│     │     ├── sounds/
│     │     ├── images/
│     │     └── fonts/
│
├── api/
│     ├── main.py
│     ├── routers/
│     ├── models/
│     └── db.py
│
└── tests/
      ├── test_engine.py
      ├── test_network.py
      └── test_api.py
```

---

# 🧠 5. Návrhové principy projektu

## 5.1 Oddělení zodpovědností (Separation of Concerns)

* engine = logika
* klient = vykreslování
* server = multiplayer
* API = přístup k výsledkům
* DB = ukládání

## 5.2 Modularita

Každá část musí být samostatně testovatelná.

## 5.3 Expandabilita

Architektura umožní přidat:

* AI hráče
* nové typy pálek
* power-upy
* animace
* turnajový režim

## 5.4 Testovatelnost

Engine bude testován samostatně pomocí PyTest:

* odraz míčku
* přičítání skóre
* trvání zápasu
* kolizní detekce

## 5.5 Síťový determinismus

Server je jediná autorita → minimalizuje cheating a desynchronizaci.

---

# 🔌 6. Komunikační protokol

Protokol je čistě JSON.

## Příklad vstupu od klienta:

```json
{
  "type": "input",
  "player_id": "p3",
  "action": "MOVE_UP"
}
```

## Příklad snapshotu od serveru:

```json
{
  "type": "snapshot",
  "timestamp": 245322.233,
  "ball": { "x": 800, "y": 400, "vx": -6, "vy": 2 },
  "paddles": [
    { "id": "A1", "x": 100, "y": 300 },
    { "id": "A2", "x": 100, "y": 500 },
    { "id": "B1", "x": 1100, "y": 320 }
  ],
  "score": { "A": 3, "B": 4 },
  "time_left": 51.3
}
```

---

# 📡 7. Ticking a synchronizace

### Hlavní smyčka:

* běží na serveru
* výpočetní krok enginu: 60×/s
* rozeslání snapshotů: 20–30×/s

### Klient:

* renderuje 60 FPS
* používá **interpolaci** mezi snapshoty

---

# 📘 8. Shrnutí architektury

MULTIPONG je:

* škálovatelný
* modulární
* dobře testovatelný
* ideální pro výuku moderního programování
* vhodný pro přidávání nových funkcí

Tento dokument bude výchozí referencí pro další fáze.



# 🏗️ MULTIPONG - Architektura Engine a Modulů

Souhrn na základě `docs/01_architecture_plan.md`

---

## 🎮 1. HLAVNÍ MODULY ENGINE (čisté OOP, bez Pygame)

Engine je **jádro logiky hry**, nezávislé na síti a grafice.

### 1.1 Základní třídy enginu:

| Třída | Zodpovědnost | Hlavní atributy/metody |
|-------|--------------|------------------------|
| **`GameState`** | Globální stav hry | teams, ball, arena, score, time_left |
| **`Ball`** | Míček | x, y, vx, vy, radius, update(), reset() |
| **`Paddle`** | Pálka | x, y, width, height, move_up(), move_down() |
| **`Team`** | Tým (A nebo B) | name, score, paddles[], color |
| **`Arena`** | Hrací plocha | width, height, boundaries, get_center() |
| **`MatchController`** | Řízení zápasu | start_match(), end_match(), reset_round() |
| **`CollisionDetector`** | Detekce kolizí | check_ball_paddle(), check_ball_walls() |

### 1.2 Pravidla enginu:

✅ **Engine nesmí obsahovat žádné Pygame volání**
✅ **Engine je nezávislý na síti**
✅ **Engine vytváří stavový snapshot (dict) pro klienty**

### 1.3 Co engine dělá:

- ✅ Počítá fyziku (pohyb míčku)
- ✅ Zpracovává kolize
- ✅ Zaznamenává skóre
- ✅ Eviduje zásahy
- ✅ Řídí trvání zápasu
- ✅ Vytváří stavový snapshot → posílaný klientům

---

## 🌐 2. NETWORK SERVER (WebSockets + asyncio)

### 2.1 Klíčové komponenty serveru:

| Komponenta | Zodpovědnost | Soubor |
|------------|--------------|--------|
| **`WebSocketManager`** | Správa WS připojení | `websocket_server.py` |
| **`PlayerSession`** | Stav hráče | `player_session.py` |
| **`LobbyHandler`** | Správa lobby a slotů | `lobby.py` |
| **`GameLoopController`** | Hlavní tick smyčka | `game_loop.py` |
| **`InputProcessor`** | Zpracování vstupů | `protocol.py` |

### 2.2 Serverová smyčka:

- **Tick rate:** 60×/s (výpočet enginu)
- **Snapshot rate:** 20-30×/s (rozeslání stavu)

### 2.3 Komunikační protokol (JSON):

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

## 💻 3. PYGAME KLIENT (Prezentační vrstva)

### 3.1 Komponenty klienta:

| Komponenta | Zodpovědnost | Soubor |
|------------|--------------|--------|
| **`NetworkClient`** | WS komunikace | `ws_client.py` |
| **`Renderer`** | Vykreslování (Pygame) | `renderer.py` |
| **`InputHandler`** | Zachytávání vstupů | `input_handler.py` |
| **`ClientState`** | Místní kopie snapshotu | `client_state.py` |
| **`InterpolationEngine`** | Plynulé vykreslování | `interpolation.py` |

### 3.2 Pravidlo klienta:

❗ **Klient nikdy nepočítá herní logiku — to dělá server.**

---

## 🔌 4. REST API VRSTVA (FastAPI)

### 4.1 Endpointy:

| Endpoint | Metoda | Účel |
|----------|--------|------|
| `/players/` | GET | Seznam hráčů |
| `/players/{id}` | GET | Detail hráče |
| `/leaderboard/` | GET | Žebříček |
| `/matches/` | POST | Uložení zápasu |
| `/matches/{id}` | GET | Detail zápasu |
| `/stats/player/{id}` | GET | Statistiky hráče |

### 4.2 Struktura API:

```
api/
├── main.py              # FastAPI aplikace
├── routers/
│   ├── players.py       # Players CRUD
│   ├── matches.py       # Matches CRUD
│   ├── leaderboard.py   # Žebříček
│   └── stats.py         # Statistiky
├── models/
│   ├── player.py        # SQLAlchemy modely
│   ├── match.py
│   └── team.py
└── db.py                # Databázové připojení
```

---

## 💾 5. DATABÁZOVÁ VRSTVA (SQLAlchemy)

### 5.1 Tabulky:

| Tabulka | Sloupce | Účel |
|---------|---------|------|
| **`players`** | id, nickname, rating, total_games | Základní data hráčů |
| **`matches`** | id, date, duration, winner_team | Historie zápasů |
| **`teams`** | id, match_id, name, score | Týmy v zápasech |
| **`player_stats`** | id, player_id, match_id, hits, misses | Statistiky |
| **`goals`** | id, match_id, team, timestamp | Góly v zápasech |

---

## 📁 6. NAVRHOVANÁ STRUKTURA SOUBORŮ

### 6.1 Engine moduly (`multipong/engine/`)

```python
multipong/engine/
├── __init__.py
├── ball.py              # class Ball
├── paddle.py            # class Paddle
├── team.py              # class Team
├── arena.py             # class Arena
├── gamestate.py         # class GameState
├── match_controller.py  # class MatchController
├── collision.py         # class CollisionDetector
└── physics.py           # Fyzikální konstanty a pomocné funkce
```

#### **ball.py**
```python
from dataclasses import dataclass

@dataclass
class Ball:
    """Míček v MULTIPONG."""
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 8.0
    
    def update(self, delta_time: float) -> None:
        """Aktualizuje pozici míčku."""
        pass
    
    def reset(self, arena_center: tuple) -> None:
        """Resetuje míček do středu."""
        pass
    
    def reverse_x(self) -> None:
        """Obrátí směr X (odraz)."""
        pass
```

#### **paddle.py**
```python
from dataclasses import dataclass

@dataclass
class Paddle:
    """Pálka v MULTIPONG."""
    id: str  # např. "A1", "B3"
    x: float
    y: float
    width: float = 10.0
    height: float = 60.0
    speed: float = 5.0
    
    def move_up(self, delta_time: float) -> None:
        pass
    
    def move_down(self, delta_time: float) -> None:
        pass
    
    def clamp_to_arena(self, arena_height: int) -> None:
        """Omezí pohyb v rámci arény."""
        pass
```

#### **team.py**
```python
from dataclasses import dataclass, field
from typing import List
from .paddle import Paddle

@dataclass
class Team:
    """Tým (A nebo B) s pálkami a skóre."""
    name: str  # "A" nebo "B"
    score: int = 0
    paddles: List[Paddle] = field(default_factory=list)
    color: tuple = (255, 255, 255)
    
    def add_paddle(self, paddle: Paddle) -> None:
        pass
    
    def increment_score(self) -> None:
        pass
```

#### **arena.py**
```python
from dataclasses import dataclass

@dataclass
class Arena:
    """Hrací plocha pro MULTIPONG."""
    width: int = 800
    height: int = 600
    
    def get_center(self) -> tuple:
        return (self.width // 2, self.height // 2)
    
    def is_out_of_bounds(self, x: float, y: float) -> bool:
        pass
```

#### **gamestate.py**
```python
from dataclasses import dataclass
from typing import Dict
from .ball import Ball
from .team import Team
from .arena import Arena

@dataclass
class GameState:
    """Globální stav hry."""
    ball: Ball
    teams: Dict[str, Team]  # {"A": Team, "B": Team}
    arena: Arena
    time_left: float = 120.0  # sekund
    is_running: bool = False
    
    def to_snapshot(self) -> dict:
        """Vytvoří JSON snapshot pro klienty."""
        return {
            "ball": {"x": self.ball.x, "y": self.ball.y},
            "paddles": [...],
            "score": {"A": self.teams["A"].score, "B": self.teams["B"].score},
            "time_left": self.time_left
        }
```

#### **match_controller.py**
```python
class MatchController:
    """Řídí průběh zápasu."""
    
    def __init__(self, gamestate: GameState):
        self.gamestate = gamestate
    
    def start_match(self) -> None:
        """Spustí zápas."""
        pass
    
    def end_match(self) -> str:
        """Ukončí zápas a vrátí vítěze."""
        pass
    
    def reset_round(self) -> None:
        """Reset po gólu."""
        pass
    
    def update_timer(self, delta_time: float) -> None:
        """Aktualizuje časovač."""
        pass
```

#### **collision.py**
```python
class CollisionDetector:
    """Detekce kolizí mezi objekty."""
    
    @staticmethod
    def check_ball_paddle(ball: Ball, paddle: Paddle) -> bool:
        """Kontroluje kolizi míčku s pálkou."""
        pass
    
    @staticmethod
    def check_ball_walls(ball: Ball, arena: Arena) -> str:
        """Kontroluje kolizi se stěnami. Vrací: 'top', 'bottom', 'left', 'right', None."""
        pass
    
    @staticmethod
    def handle_collision(ball: Ball, paddle: Paddle) -> None:
        """Zpracuje kolizi (změní rychlost míčku)."""
        pass
```

---

### 6.2 Network Server (`multipong/network/server/`)

```python
multipong/network/server/
├── __init__.py
├── websocket_server.py   # WebSocketManager
├── game_loop.py          # GameLoopController
├── player_session.py     # PlayerSession
├── lobby.py              # LobbyHandler
├── protocol.py           # InputProcessor, message schemas
└── config.py             # Server config
```

---

### 6.3 Network Client (`multipong/network/client/`)

```python
multipong/network/client/
├── __init__.py
├── ws_client.py          # NetworkClient (WebSocket klient)
├── message_decoder.py    # Dekódování zpráv
└── interpolation.py      # InterpolationEngine
```

---

### 6.4 UI/Rendering (`multipong/ui/`)

```python
multipong/ui/
├── __init__.py
├── renderer.py           # Renderer (Pygame)
├── input_handler.py      # InputHandler
├── client_state.py       # ClientState
└── sprites/              # Obrázky, fonty
```

---

### 6.5 API (`api/`)

```python
api/
├── __init__.py
├── main.py               # FastAPI aplikace
├── routers/
│   ├── __init__.py
│   ├── players.py        # Players CRUD
│   ├── matches.py        # Matches CRUD
│   ├── leaderboard.py    # Žebříček
│   └── stats.py          # Statistiky
├── models/
│   ├── __init__.py
│   ├── player.py         # SQLAlchemy Player model
│   ├── match.py          # SQLAlchemy Match model
│   └── team.py           # SQLAlchemy Team model
└── db.py                 # Database connection
```

---

## 🎯 7. NÁVRHOVÉ PRINCIPY

### 7.1 Oddělení zodpovědností (Separation of Concerns)

- **Engine** = čistá logika
- **Klient** = vykreslování
- **Server** = multiplayer
- **API** = přístup k výsledkům
- **DB** = ukládání

### 7.2 Modularita

✅ Každá část je samostatně testovatelná

### 7.3 Expandabilita

Architektura umožní přidat:
- AI hráče
- Nové typy pálek
- Power-upy
- Animace
- Turnajový režim

### 7.4 Síťový determinismus

✅ **Server je jediná autorita** → minimalizuje cheating a desynchronizaci

---

## 📊 8. KOMPLETNÍ PŘEHLED MODULŮ

### Engine Core (7 tříd)
1. ✅ `Ball` - míček s fyzikou
2. ✅ `Paddle` - pálka s pohybem
3. ✅ `Team` - tým se skóre
4. ✅ `Arena` - hrací plocha
5. ✅ `GameState` - globální stav
6. ✅ `MatchController` - řízení zápasu
7. ✅ `CollisionDetector` - kolize

### Network Server (5 komponent)
1. ✅ `WebSocketManager` - WS správa
2. ✅ `PlayerSession` - session hráče
3. ✅ `LobbyHandler` - lobby systém
4. ✅ `GameLoopController` - tick smyčka
5. ✅ `InputProcessor` - zpracování vstupů

### Network Client (4 komponenty)
1. ✅ `NetworkClient` - WS klient
2. ✅ `Renderer` - Pygame rendering
3. ✅ `InputHandler` - vstupy
4. ✅ `InterpolationEngine` - interpolace

### API (4 routery)
1. ✅ `players` - CRUD hráčů
2. ✅ `matches` - CRUD zápasů
3. ✅ `leaderboard` - žebříček
4. ✅ `stats` - statistiky

### Database (5 modelů)
1. ✅ `Player` - hráči
2. ✅ `Match` - zápasy
3. ✅ `Team` - týmy
4. ✅ `PlayerStats` - statistiky
5. ✅ `Goal` - góly

---

## 🚀 9. DALŠÍ KROKY

### Fáze implementace:

1. ✅ **Fáze 1**: Základní struktura (HOTOVO)
2. 📝 **Fáze 2**: Engine - všech 7 tříd
3. 📝 **Fáze 3**: Multipong logika (4v4)
4. 📝 **Fáze 4**: Async WebSocket server
5. 📝 **Fáze 5**: Síťová synchronizace
6. 📝 **Fáze 6**: Pygame klient s interpolací
7. 📝 **Fáze 7**: Database integrace
8. 📝 **Fáze 8**: REST API
9. 📝 **Fáze 9**: AI hráči
10. 📝 **Fáze 10**: Turnajový systém

---

**📚 Zdroj:** `docs/01_architecture_plan.md`

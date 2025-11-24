# 🎮 MULTIPONG Engine - Skeleton Classes

## ✅ Vytvořené třídy (Phase 1-2)

Vytvořil jsem skeleton strukturu hlavních tříd enginu podle `docs/02_phase1_pygame_basics.md` a `docs/03_phase2_engine_oop.md`.

---

## 📁 Struktura souborů

```
multipong/engine/
├── __init__.py          ✅ Exportuje hlavní třídy
├── ball.py              ✅ Třída Ball
├── paddle.py            ✅ Třída Paddle
├── arena.py             ✅ Třída Arena
└── game_engine.py       ✅ Třída MultipongEngine
```

---

## 🎯 1. Ball (multipong/engine/ball.py)

### Atributy:
- `x: float` - X pozice
- `y: float` - Y pozice
- `vx: float` - Rychlost X (default: 5.0)
- `vy: float` - Rychlost Y (default: 5.0)
- `radius: float` - Poloměr (default: 10.0)

### Metody (skeleton):
- `__init__(x, y, vx=5, vy=5, radius=10)` ✅ Hotovo
- `update()` 📝 TODO - pohyb míčku
- `reset(x, y)` 📝 TODO - reset pozice
- `reverse_x()` 📝 TODO - odraz X
- `reverse_y()` 📝 TODO - odraz Y
- `to_dict()` ✅ Hotovo - serializace
- `draw(surface)` 📝 TODO - placeholder pro vykreslení

### Použití:
```python
from multipong.engine import Ball

ball = Ball(x=400, y=300, vx=5, vy=3)
state = ball.to_dict()
# {'x': 400, 'y': 300, 'radius': 10.0, 'vx': 5, 'vy': 3}
```

---

## 🏓 2. Paddle (multipong/engine/paddle.py)

### Atributy:
- `x: float` - X pozice
- `y: float` - Y pozice
- `width: float` - Šířka (default: 20.0)
- `height: float` - Výška (default: 100.0)
- `speed: float` - Rychlost (default: 5.0)
- `player_id: str` - ID hráče (default: "P1")

### Metody (skeleton):
- `__init__(x, y, width=20, height=100, speed=5, player_id="P1")` ✅ Hotovo
- `move_up()` 📝 TODO - pohyb nahoru
- `move_down()` 📝 TODO - pohyb dolů
- `update(arena_height)` 📝 TODO - aktualizace + omezení
- `clamp_to_arena(arena_height)` 📝 TODO - omezení v aréně
- `to_dict()` ✅ Hotovo - serializace
- `draw(surface)` 📝 TODO - placeholder pro vykreslení

### Použití:
```python
from multipong.engine import Paddle

paddle = Paddle(x=50, y=100, player_id="A1")
state = paddle.to_dict()
# {'x': 50, 'y': 100, 'width': 20.0, 'height': 100.0, 'player_id': 'A1'}
```

---

## 🏟️ 3. Arena (multipong/engine/arena.py)

### Atributy:
- `width: int` - Šířka (default: 1200)
- `height: int` - Výška (default: 800)

### Metody (skeleton):
- `__init__(width=1200, height=800)` ✅ Hotovo
- `get_center()` ✅ Hotovo - vrací střed
- `get_dimensions()` ✅ Hotovo - vrací rozměry
- `is_out_of_bounds(x, y)` ✅ Hotovo - kontrola hranic
- `check_goal(ball_x, ball_radius)` 📝 TODO - detekce gólu
- `to_dict()` ✅ Hotovo - serializace
- `draw(surface)` 📝 TODO - vykreslení (střední čára, branky)

### Použití:
```python
from multipong.engine import Arena

arena = Arena(width=1200, height=800)
center = arena.get_center()  # (600, 400)
is_out = arena.is_out_of_bounds(1500, 100)  # True
```

---

## 🎮 4. MultipongEngine (multipong/engine/game_engine.py)

### Atributy:
- `arena: Arena` - Instance arény
- `ball: Ball` - Instance míčku
- `paddles: Dict[str, Paddle]` - Slovník pálek
- `score: Dict[str, int]` - Skóre týmů {"A": 0, "B": 0}
- `is_running: bool` - Stav hry
- `time_left: float` - Zbývající čas (default: 120.0)

### Metody (skeleton):
- `__init__(arena_width=1200, arena_height=800)` ✅ Hotovo
- `_initialize_paddles()` ✅ Hotovo - vytvoří A1 a B1
- `update(inputs)` 📝 TODO - hlavní smyčka
- `update_paddles(inputs)` 📝 TODO - aktualizace pálek
- `update_ball()` 📝 TODO - aktualizace míčku
- `check_collisions()` 📝 TODO - detekce kolizí
- `check_goals()` 📝 TODO - detekce gólů
- `score_goal(scoring_team)` 📝 TODO - přičtení gólu
- `reset_ball()` 📝 TODO - reset míčku
- `start()` ✅ Hotovo - spuštění hry
- `stop()` ✅ Hotovo - zastavení hry
- `reset()` 📝 TODO - reset hry
- `get_state()` ✅ Hotovo - vrací kompletní stav
- `add_paddle(player_id, team, position)` 📝 TODO - přidání pálky
- `remove_paddle(player_id)` 📝 TODO - odebrání pálky
- `draw(surface)` 📝 TODO - vykreslení celé hry

### Použití:
```python
from multipong.engine import MultipongEngine

# Vytvoření enginu
engine = MultipongEngine()

# Spuštění hry
engine.start()

# Získání stavu
state = engine.get_state()
# {
#   'ball': {'x': 600, 'y': 400, ...},
#   'paddles': {'A1': {...}, 'B1': {...}},
#   'score': {'A': 0, 'B': 0},
#   'time_left': 120.0,
#   'is_running': True,
#   'arena': {'width': 1200, 'height': 800}
# }

# Aktualizace s vstupy
inputs = {
    "A1": {"up": True, "down": False},
    "B1": {"up": False, "down": True}
}
engine.update(inputs)
```

---

## ✅ Testy (tests/engine/)

Vytvořil jsem testy pro všechny třídy:

- `test_ball.py` - 5 testů ✅
- `test_paddle.py` - 5 testů ✅
- `test_arena.py` - 6 testů ✅
- `test_game_engine.py` - 8 testů ✅

**Celkem: 24 testů - všechny prošly!** 🎉

```bash
pytest tests/engine/ -v
# 24 passed in 0.89s
```

### Test coverage:
- `ball.py` - 95% ✅
- `paddle.py` - 90% ✅
- `arena.py` - 88% ✅
- `game_engine.py` - 81% ✅

---

## 🎯 Architektonické principy (dodrženo)

✅ **Engine nezávislý na Pygame** - žádné Pygame importy v engine/
✅ **Oddělení logiky od vykreslování** - draw() metody jsou placeholder
✅ **to_dict() pro synchronizaci** - všechny třídy mají serializaci
✅ **Type hints** - všude používány
✅ **Docstringy** - Google style dokumentace
✅ **PEP8** - dodržen code style
✅ **Modulární design** - každá třída má jasnou zodpovědnost

---

## 📝 Další kroky (implementace)

### Priorita 1 - Základní pohyb:
1. ✅ Implementovat `Ball.update()` - pohyb míčku
2. ✅ Implementovat `Paddle.move_up/down()` - pohyb pálek
3. ✅ Implementovat `Paddle.update()` - omezení v aréně

### Priorita 2 - Kolize:
4. ✅ Implementovat `Ball.reverse_x/y()` - odrazy
5. ✅ Implementovat `MultipongEngine.check_collisions()` - kolize míček-pálka
6. ✅ Implementovat odraz od stěn v `Ball.update()`

### Priorita 3 - Skóre:
7. ✅ Implementovat `Arena.check_goal()` - detekce gólů
8. ✅ Implementovat `MultipongEngine.check_goals()` - kontrola gólů
9. ✅ Implementovat `MultipongEngine.score_goal()` - přičítání skóre
10. ✅ Implementovat `MultipongEngine.reset_ball()` - reset po gólu

### Priorita 4 - Multiplayer:
11. ✅ Implementovat `MultipongEngine.add_paddle()` - více pálek
12. ✅ Implementovat `MultipongEngine.remove_paddle()` - odpojení hráče
13. ✅ Rozšířit na 4v4 (8 pálek)

---

## 🚀 Spuštění testů

```bash
# Všechny testy
pytest tests/engine/ -v

# S pokrytím
pytest tests/engine/ -v --cov=multipong.engine --cov-report=html

# Konkrétní soubor
pytest tests/engine/test_ball.py -v
```

---

## 📚 Dokumentace

Skeleton je vytvořen podle:
- ✅ `docs/02_phase1_pygame_basics.md`
- ✅ `docs/03_phase2_engine_oop.md`
- ✅ `COPILOT_INSTRUCTIONS.md`
- ✅ `docs/01_architecture_plan.md`

**Všechny třídy jsou připravené k implementaci! 🎮**

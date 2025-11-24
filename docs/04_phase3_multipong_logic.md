# **04_phase3_multipong_logic.md — MULTIPONG logika: týmy, více pálek, zóny a statistiky**

## 🎯 1. Cíle fáze 3

V této fázi vybudujeme strukturu, která dělá z obyčejného Pongu **komplexní týmovou hru**:

* přidáme **týmy A a B**
* každý tým může mít **1–4 pálky**
* každá pálka má svou **zónu** (100/200/300/400 px od zadní stěny)
* přidáme **branky** na obou stranách
* vytvoříme **statistiky hráčů**
* engine začne pracovat se **seznamy pálek**
* připravíme systém, který později snadno přejde na multiplayer

Tato fáze vytváří plnou *logickou kostru* MULTIPONGU.
Grafické věci zatím děláme jednoduše – UI se vylepší později.

---

# 🧠 2. Proč tato fáze existuje?

MULTIPONG má:

* více hráčů v jednom týmu
* více pálek v různých vzdálenostech od zdi
* zóny a branky
* statistiky, zásahy, góly
* připravenou strukturu pro síťový multiplayer

Proto potřebujeme engine přepracovat:

* od **paddle_left / paddle_right** → k **seznamům pálek**
* od **jednoduché kolize** → ke **kolizi ve více úrovních**
* od **jednoduchého skóre** → ke **komplexním statistikám**

---

# 🧱 3. Nové třídy v engine

Vytvoříme tyto třídy:

```
Team
Paddle (upravená verze)
PlayerStats
GoalZone
MultipongEngine (náhrada původního GameEngine)
```

---

# 🟦 4. Třída `PlayerStats`

Každá pálka = jeden hráč → uchováme statistiku:

* počet zásahů míčku
* počet obdržených gólů (pokud míček spadne do její sekce)
* počet vstřelených gólů (její tým)

`soubor: multipong/engine/player_stats.py`

```python
class PlayerStats:
    def __init__(self, player_id):
        self.player_id = player_id
        self.hits = 0
        self.goals_scored = 0
        self.goals_received = 0

    def record_hit(self):
        self.hits += 1

    def record_goal_scored(self):
        self.goals_scored += 1

    def record_goal_received(self):
        self.goals_received += 1

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "hits": self.hits,
            "goals_scored": self.goals_scored,
            "goals_received": self.goals_received
        }
```

---

# 🟩 5. Úprava třídy `Paddle` – přidání zón

Každá pálka má:

* svou **x-pozici** (vzdálenost od zdi)
* povolenou **zónu** v rámci které se pohybuje

Např. pro tým vlevo:

* pálka 1 → x = 100
* pálka 2 → x = 200
* pálka 3 → x = 300
* pálka 4 → x = 400

Vytvoříme konstruktor:

```python
class Paddle:
    def __init__(self, x, y, zone_top, zone_bottom, stats, width=20, height=100, speed=5):
        self.x = x
        self.y = y
        self.zone_top = zone_top
        self.zone_bottom = zone_bottom
        self.width = width
        self.height = height
        self.speed = speed
        self.stats = stats
```

Upravíme update:

```python
def update(self):
    # omezení na zónu
    if self.y < self.zone_top:
        self.y = self.zone_top
    if self.y + self.height > self.zone_bottom:
        self.y = self.zone_bottom - self.height
```

---

# 🟥 6. Třída `Team` – sdružuje hráče (pálky)

Soubor: `multipong/engine/team.py`

```python
class Team:
    def __init__(self, name, paddles):
        self.name = name
        self.paddles = paddles  # list[Paddle]
        self.score = 0

    def add_score(self):
        self.score += 1

    def to_dict(self):
        return {
            "name": self.name,
            "score": self.score,
            "paddles": [p.stats.to_dict() for p in self.paddles]
        }
```

---

# 🟧 7. Třída `GoalZone` – branka

Branka je pásmo na straně hřiště:

* má X-pozici (na levé nebo pravé straně)
* má výšku (např. 200 px)
* má střed (např. střed obrazovky)
* míček skrz ni = gól

Soubor: `multipong/engine/goal_zone.py`

```python
class GoalZone:
    def __init__(self, x, top, bottom):
        self.x = x
        self.top = top
        self.bottom = bottom

    def check_goal(self, ball):
        # míček prolétl x-souřadnicí branky?
        if abs(ball.x - self.x) < ball.radius:
            if self.top <= ball.y <= self.bottom:
                return True
        return False
```

---

# 🟦 8. Nový engine: `MultipongEngine`

Toto je hlavní třída.
Nahradí dřívější `GameEngine`.

---

## 8.1 Konstruktor

Vytvoří:

* hřiště
* míček
* 4 pálky vlevo a 4 vpravo
* 2 týmy
* 2 branky

```python
from .paddle import Paddle
from .ball import Ball
from .team import Team
from .goal_zone import GoalZone
from .player_stats import PlayerStats
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

class MultipongEngine:

    ZONE_HEIGHT = WINDOW_HEIGHT // 4

    def __init__(self):
        self.ball = Ball(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, vx=6, vy=4)

        self.team_left = self._create_team(
            "A",
            x_positions=[100, 200, 300, 400]
        )
        self.team_right = self._create_team(
            "B",
            x_positions=[WINDOW_WIDTH - 100, WINDOW_WIDTH - 200, WINDOW_WIDTH - 300, WINDOW_WIDTH - 400]
        )

        # Branky
        goal_size = 200
        self.goal_left = GoalZone(0, WINDOW_HEIGHT//2 - goal_size//2, WINDOW_HEIGHT//2 + goal_size//2)
        self.goal_right = GoalZone(WINDOW_WIDTH, WINDOW_HEIGHT//2 - goal_size//2, WINDOW_HEIGHT//2 + goal_size//2)
```

---

## 8.2 Metoda `_create_team`

```python
def _create_team(self, name, x_positions):
    paddles = []
    for i, x in enumerate(x_positions):
        zone_top = i * self.ZONE_HEIGHT
        zone_bottom = zone_top + self.ZONE_HEIGHT
        stats = PlayerStats(f"{name}{i+1}")
        paddle = Paddle(x, WINDOW_HEIGHT//2 - 50, zone_top, zone_bottom, stats)
        paddles.append(paddle)

    return Team(name, paddles)
```

---

## 8.3 Hlavní update logika

Zpracuje:

* vstupy hráčů
* pohyb míče
* kolize s pálkami
* detekci gólu

```python
def update(self, paddle_inputs):
    """
    paddle_inputs = dict { "A1": {"up": bool, "down": bool}, ... }
    """

    # --- pohyb pálek ---
    for team in [self.team_left, self.team_right]:
        for paddle in team.paddles:
            pid = paddle.stats.player_id
            if pid in paddle_inputs:
                if paddle_inputs[pid]["up"]:
                    paddle.move_up()
                if paddle_inputs[pid]["down"]:
                    paddle.move_down()
            paddle.update()

    # --- pohyb míče ---
    self.ball.update()

    # --- kolize s pálkami ---
    for team in [self.team_left, self.team_right]:
        for paddle in team.paddles:
            if self._check_paddle_collision(paddle):
                paddle.stats.record_hit()
                self.ball.vx *= -1

    # --- gól vlevo ---
    if self.goal_left.check_goal(self.ball):
        self.team_right.add_score()
        self._reset_ball()

    # --- gól vpravo ---
    if self.goal_right.check_goal(self.ball):
        self.team_left.add_score()
        self._reset_ball()
```

---

## 8.4 Detekce kolize

```python
def _check_paddle_collision(self, paddle):
    return (
        paddle.x <= self.ball.x <= paddle.x + paddle.width and
        paddle.y <= self.ball.y <= paddle.y + paddle.height
    )
```

---

## 8.5 Reset míčku

```python
def _reset_ball(self):
    self.ball.x = WINDOW_WIDTH // 2
    self.ball.y = WINDOW_HEIGHT // 2
    self.ball.vx *= -1
```

---

## 8.6 Export stavu hry pro UI nebo klienta

```python
def get_state(self):
    return {
        "ball": self.ball.to_dict(),
        "team_left": self.team_left.to_dict(),
        "team_right": self.team_right.to_dict(),
        "goal_left": {"top": self.goal_left.top, "bottom": self.goal_left.bottom},
        "goal_right": {"top": self.goal_right.top, "bottom": self.goal_right.bottom},
    }
```

---

# 🎮 9. Ukázka použití v `main.py` (lokální hra)

Tady už máme 8 pálkařů (4 na každé straně):

```python
inputs = {
    "A1": {"up": keys[K_w], "down": keys[K_s]},
    "B1": {"up": keys[K_UP], "down": keys[K_DOWN]},
    # ostatní lze doplnit třeba AI
}

engine.update(inputs)
state = engine.get_state()
```

Brian (řiďící Pygame) pak vykreslí každý paddle ze seznamů.

---

# 🧪 10. Mini výzvy pro studenty

### 🔹 1) Přidej jednoduché "AI" pro volné pálky

Pálka sleduje pozici míčku.

### 🔹 2) Vytvoř proměnnou velikost branky

Parametr přidáme do `config.json`.

### 🔹 3) Přidej „přestávku“ po gólu

Odpočet 1 sekunda před opětovným vhazováním.

### 🔹 4) Copilot prompt:

> „Navrhni a implementuj do MultipongEngine mechaniku power-upů, které zvyšují rychlost pálky po zásahu míčku.“

---


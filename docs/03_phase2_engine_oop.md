# **03_phase2_engine_oop.md — OOP návrh herního enginu**

## 🎯 1. Cíle fáze 2

Ve fázi 1 jsme vytvořili jednoduché Pygame okno a první pohyb pálky.
Nyní se posuneme na vyšší úroveň:

* přepíšeme kód do **objektově orientované podoby**
* naučíme se správný návrh tříd
* oddělíme **logiku hry** (engine) od **vykreslování** (UI)
* připravíme jádro, které bude později fungovat i bez Pygame

---

# 🧠 2. Proč OOP?

Hra MULTIPONG se bude postupně rozrůstat, proto potřebujeme kód:

* přehledný
* rozšiřitelný
* snadno testovatelný
* nezávislý na Pygame (aby mohl běžet na serveru)

Správný OOP návrh nám to umožní.

---

# 🧱 3. Nová adresářová struktura

Do složky `multipong/engine/` vložíme třídy:

```
multipong/
│
├── multipong/
│     ├── main.py
│     ├── settings.py
│     ├── engine/
│     │     ├── ball.py
│     │     ├── paddle.py
│     │     ├── arena.py
│     │     └── game_engine.py
│     └── ui/
│          └── renderer.py
│
└── docs/
      └── 03_phase2_engine_oop.md
```

---

# ⚙️ 4. Návrh tříd

V této fázi definujeme základní logické části hry.

## **4.1 Třída `Paddle` (pálka)**

* pozice
* velikost
* rychlost
* metoda `move_up()`
* metoda `move_down()`
* metoda `update()`
* metoda `to_dict()` pro budoucí synchronizaci se serverem

### Verze **bez Pygame**, čistá logika:

`multipong/engine/paddle.py`:

```python
from settings import WINDOW_HEIGHT

class Paddle:
    """
    Logická reprezentace jedné pálky.
    Nezávislá na Pygame. Slouží výhradně pro engine.
    """

    def __init__(self, x, y, width=20, height=100, speed=5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def move_up(self):
        self.y -= self.speed

    def move_down(self):
        self.y += self.speed

    def update(self):
        """Omezí pohyb pálky, aby nevyjela z hřiště."""
        if self.y < 0:
            self.y = 0
        if self.y + self.height > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.height

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }
```

---

## **4.2 Třída `Ball` (míček)**

* pozice
* rychlost
* metoda `update()`
* odraz od horní/dolní stěny
* metoda `to_dict()`

`multipong/engine/ball.py`:

```python
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

class Ball:
    """Logická reprezentace míčku – bez grafiky."""

    def __init__(self, x, y, vx=5, vy=5, radius=10):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius

    def update(self):
        """Posun míčku a odraz od horní/dolní stěny."""
        self.x += self.vx
        self.y += self.vy

        # Odraz od horní/dolní stěny
        if self.y - self.radius < 0 or self.y + self.radius > WINDOW_HEIGHT:
            self.vy = -self.vy

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius
        }
```

---

## **4.3 Třída `Arena` (hřiště)**

Zatím jednoduchá – později bude obsahovat:

* branky
* zóny
* výpočet skóre
* generování více pálek

`multipong/engine/arena.py`:

```python
class Arena:
    """
    Reprezentace herního hřiště.
    Zatím jednoduchá; později zde budou branky, zóny, překážky.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
```

---

## **4.4 Třída `GameEngine`**

Srdce celé hry:

* drží instance Ball a Paddle
* zpracuje logiku hry
* aktualizuje objekty
* připraví stav pro Pygame/UI

`multipong/engine/game_engine.py`:

```python
from .ball import Ball
from .paddle import Paddle
from .arena import Arena
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

class GameEngine:
    """
    Hlavní logický modul hry – NEZÁVISLÝ NA PYGAME.
    """

    def __init__(self):
        self.arena = Arena(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.paddle_left = Paddle(50, WINDOW_HEIGHT // 2 - 50)
        self.paddle_right = Paddle(WINDOW_WIDTH - 70, WINDOW_HEIGHT // 2 - 50)

    def update(self, left_up, left_down, right_up, right_down):
        """
        Aktualizace logiky hry:
        - zpracuje vstupy
        - posune objekty
        - detekuje odrazy od pálek
        """

        # --- pohyb pálek ---
        if left_up:
            self.paddle_left.move_up()
        if left_down:
            self.paddle_left.move_down()
        if right_up:
            self.paddle_right.move_up()
        if right_down:
            self.paddle_right.move_down()

        self.paddle_left.update()
        self.paddle_right.update()

        # --- pohyb míčku ---
        self.ball.update()

        # --- jednoduchá kolize s pálkami ---
        if (self.ball.x - self.ball.radius < self.paddle_left.x + self.paddle_left.width and
            self.paddle_left.y < self.ball.y < self.paddle_left.y + self.paddle_left.height):
            self.ball.vx = abs(self.ball.vx)

        if (self.ball.x + self.ball.radius > self.paddle_right.x and
            self.paddle_right.y < self.ball.y < self.paddle_right.y + self.paddle_right.height):
            self.ball.vx = -abs(self.ball.vx)

    def get_state(self):
        """Vrátí kompletní stav hry jako slovník."""
        return {
            "ball": self.ball.to_dict(),
            "paddle_left": self.paddle_left.to_dict(),
            "paddle_right": self.paddle_right.to_dict()
        }
```

---

# 🎨 5. Přechod UI na novou logiku – update `main.py`

`multipong/main.py`:

```python
import pygame
from settings import *
from engine.game_engine import GameEngine

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("MULTIPONG – Phase 2")
    clock = pygame.time.Clock()

    engine = GameEngine()

    running = True
    while running:
        left_up = left_down = right_up = right_down = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        left_up = keys[pygame.K_w]
        left_down = keys[pygame.K_s]
        right_up = keys[pygame.K_UP]
        right_down = keys[pygame.K_DOWN]

        # LOGICKÁ AKTUALIZACE
        engine.update(left_up, left_down, right_up, right_down)
        state = engine.get_state()

        # VYKRESLOVÁNÍ
        screen.fill(COLOR_BACKGROUND)

        # pálky
        p1 = state["paddle_left"]
        p2 = state["paddle_right"]
        pygame.draw.rect(screen, COLOR_PADDLE, (p1["x"], p1["y"], p1["width"], p1["height"]))
        pygame.draw.rect(screen, COLOR_PADDLE, (p2["x"], p2["y"], p2["width"], p2["height"]))

        # míček
        b = state["ball"]
        pygame.draw.circle(screen, (200, 80, 80), (int(b["x"]), int(b["y"])), b["radius"])

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
```

---

# 🧪 6. Mini výzvy pro studenty

### 🔹 1) Zrychlení míčku po odrazu

Po každé kolizi mírně zvyš rychlost `vx` nebo `vy`.

### 🔹 2) Přidej resetovací metodu

Metoda `reset()` v engine, která vrátí míček a pálky na začátek.

### 🔹 3) Přidej jednoduché skóre

Engine sleduje, kdy míček proletí za levou nebo pravou hranou.

### 🔹 4) Doporučený Copilot prompt

> „Vytvoř metodu `check_score()` do GameEngine, která detekuje gól a resetuje míček.“


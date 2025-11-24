# **02_phase1_pygame_basics.md — Základy Pygame a první herní smyčka**

## 🎯 1. Cíle fáze 1

V této fázi se naučíš:

* vytvořit základní herní okno v Pygame
* pochopit hlavní smyčku hry (game loop)
* zpracovávat události (klávesnice, zavření okna)
* vykreslovat objekty na obrazovku
* řídit FPS (frames per second)
* vytvořit první jednoduchý pohyb objektu

To vše vytváří základ pro budoucí herní engine MULTIPONG.

---

# 🧱 2. Co budeme vytvářet v této fázi

### Na konci fáze 1 budeš mít:

✔ běžící Pygame okno 1200×800
✔ hlavní herní smyčku
✔ jednoduchý obdélník ovládaný klávesami nahoru/dolů
✔ zvláštní modul pro nastavení (`settings.py`)
✔ základní strukturu kódu připravenou pro další fáze

Tento základ později nahradíme skutečným enginem, ale zatím stačí jednoduchá kostra.

---

# 📁 3. Struktura projektu v této fázi

Doporučená struktura složek:

```
multipong/
│
├── multipong/
│     ├── main.py
│     ├── settings.py
│     └── ui/
│          └── renderer.py   (zatím prázdný – připravený pro další fáze)
│
└── docs/
      └── 02_phase1_pygame_basics.md
```

---

# ⚙️ 4. Soubor `settings.py`

Vytvoříme jednoduchý modul s konstantami, které budeme používat v různých částech kódu.
Učí nás to oddělovat „konfigurační“ hodnoty od logiky hry.

`multipong/settings.py`:

```python
# -------------------------------
# Globální nastavení hry MULTIPONG
# -------------------------------

# Rozměry okna
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Barvy (RGB)
COLOR_BACKGROUND = (30, 30, 30)
COLOR_PADDLE = (200, 200, 200)

# FPS limit
FPS = 60
```

---

# ▶️ 5. Základní okno a smyčka – soubor `main.py`

Kód níže je první verze herní smyčky MULTIPONG.

`multipong/main.py`:

```python
import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BACKGROUND, COLOR_PADDLE, FPS

def main():
    pygame.init()

    # Okno
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("MULTIPONG – Phase 1")

    # Hodiny pro řízení FPS
    clock = pygame.time.Clock()

    # Jednoduchý obdélník (pálka) pro demonstraci
    paddle_width = 20
    paddle_height = 100
    paddle_x = 50
    paddle_y = WINDOW_HEIGHT // 2 - paddle_height // 2
    paddle_speed = 5

    running = True
    while running:

        # --- ZPRACOVÁNÍ UDÁLOSTÍ ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- LOGIKA POHYBU ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            paddle_y -= paddle_speed
        if keys[pygame.K_DOWN]:
            paddle_y += paddle_speed

        # omezení pohybu na okno
        paddle_y = max(0, min(WINDOW_HEIGHT - paddle_height, paddle_y))

        # --- VYKRESLOVÁNÍ ---
        screen.fill(COLOR_BACKGROUND)
        pygame.draw.rect(screen, COLOR_PADDLE, (paddle_x, paddle_y, paddle_width, paddle_height))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
```

---

# 🎮 6. Jak to funguje?

### ✔ Inicializace

`pygame.init()` nastaví všechny moduly Pygame.

### ✔ Okno

`pygame.display.set_mode()` vytvoří hlavní herní obrazovku.

### ✔ Smyčka hry

Každý Pygame program obsahuje tzv. **game loop**:

1. zpracování událostí
2. aktualizace stavu hry
3. vykreslení na displej
4. omezení FPS

### ✔ Řízení FPS

`clock.tick(FPS)` zajistí, že smyčka poběží stabilně (např. 60x za sekundu).

### ✔ Zpracování vstupu

`pygame.key.get_pressed()` umožní kontrolovat stisk kláves každým snímkem.

---

# 🧠 7. Co vše se zde už učíme

* principy nekonečné smyčky
* oddělení vykreslování a logiky
* správa vstupů
* práce s konstantami v `settings.py`
* příprava struktury projektu pro větší aplikaci
* základy OOP (které později doplníme)

---

# 🧪 8. Mini výzva pro studenty (volitelné úkoly)

Tyto úkoly můžeš zadat studentům jako samostatné rozšíření:

### 🔹 1) Přidej druhou pálku – ovládání W/S

```python
if keys[pygame.K_w]: left_paddle_y -= paddle_speed
if keys[pygame.K_s]: left_paddle_y += paddle_speed
```

### 🔹 2) Přidej jednoduchý míček (bez kolizí)

### 🔹 3) Změň barvu pozadí pomocí klávesy B

Nápověda: používej `pygame.KEYDOWN`.

### 🔹 4) Doporučený Copilot prompt

> „Napiš jednoduchou třídu Paddle pro Pygame, která má metody update(), draw() a omezuje pohyb na herní okno.“



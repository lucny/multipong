# **07_phase6_settings_and_config.md — Konfigurační systém MULTIPONG**

## 🎯 1. Cíle fáze 6

V této fázi vytvoříme robustní systém nastavení hry.
Konkrétně:

* zavést **externí konfigurační soubor** (`config.json`)
* umožnit měnit parametry hry **bez přepisování kódu**
* vytvořit modul `config_loader.py`
* zapojit konfiguraci do enginu, serveru i klienta
* připravit půdu pro pozdější *uživatelské menu nastavení*

Projekt MULTIPONG tím získá profesionální flexibilitu.

---

# 🧠 2. Proč konfigurační soubor?

Protože budeme potřebovat dynamicky měnit:

* rychlosti míčku
* rychlosti pálek
* velikosti branek
* počet hráčů (1–4 na tým)
* velikosti pálek
* barvy UI
* délku zápasu
* sílu odrazu
* parametry serveru (tick rate)
* parametry renderu (FPS)

Chceme, aby studenti nebo hráči zvládli změnit nastavení **bez úpravy Python kódu**.

---

# 📁 3. Nové soubory pro fázi 6

```
multipong/
│
├── multipong/
│     ├── config/
│     │     ├── config.json
│     │     └── config_loader.py
│     │
│     ├── settings.py   (ponecháme pro globální konstanty)
│     └── ...
│
└── docs/
      └── 07_phase6_settings_and_config.md
```

---

# 🟦 4. Obsah konfiguračního souboru – `config.json`

Výchozí konfigurace:

`multipong/config/config.json`

```json
{
  "game": {
    "arena_width": 1200,
    "arena_height": 800,
    "match_duration_seconds": 180
  },

  "paddles": {
    "count_per_team": 4,
    "width": 20,
    "height": 100,
    "speed": 6
  },

  "ball": {
    "radius": 10,
    "speed_x": 6,
    "speed_y": 4,
    "speed_increment_on_hit": 0.2
  },

  "goals": {
    "size": 200
  },

  "server": {
    "tick_rate": 60
  },

  "client": {
    "fps": 60
  }
}
```

Toto je jen příklad – systém je snadno rozšiřitelný.

---

# 🟧 5. Loader konfigurace – `config_loader.py`

Hlavní úkoly loaderu:

* načíst JSON
* validovat obsah
* zpřístupnit config jako slovník nebo třídu
* umožnit predikci pro Copilot (jasný datový model)

`soubor: multipong/config/config_loader.py`

```python
import json
import os

CONFIG = {}

def load_config():
    """Načte config.json do globální proměnné CONFIG."""
    global CONFIG

    path = os.path.join(os.path.dirname(__file__), "config.json")

    with open(path, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)

    return CONFIG

def get(path, default=None):
    """
    Bezpečné získání hodnoty z konfigurace.
    Path ve tvaru 'section.key'
    Např.: get("ball.radius")
    """
    parts = path.split(".")
    value = CONFIG

    for p in parts:
        if p not in value:
            return default
        value = value[p]

    return value
```

---

# 🟩 6. Úprava `settings.py`

`settings.py` bude nově obsahovat jen *globální konstanty*, které se nemění podle hry (např. barvy).

Konfigurace hry se bude načítat právě přes `config_loader`.

`multipong/settings.py`:

```python
# barvy
COLOR_BACKGROUND = (30, 30, 30)
COLOR_PADDLE = (200, 200, 200)
COLOR_BALL = (200, 80, 80)
```

---

# 🟥 7. Integrace konfigurace do enginu

Příklad úpravy konstruktoru míčku:

Předtím:

```python
self.ball = Ball(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, vx=6, vy=4)
```

Nově:

```python
from config.config_loader import get

ball_radius = get("ball.radius")
ball_speed_x = get("ball.speed_x")
ball_speed_y = get("ball.speed_y")

self.ball = Ball(
    self.arena_width // 2,
    self.arena_height // 2,
    vx=ball_speed_x,
    vy=ball_speed_y,
    radius=ball_radius
)
```

### Stejně upravíme:

* velikost pálky
* rychlost pálky
* počet hráčů na tým
* velikost branek

---

# 🟫 8. Integrace do serveru – tick rate

V dokumentu fáze 4 jsme měli fixní `1/60` sekundy.

Teď:

```python
tick_rate = get("server.tick_rate", 60)
await asyncio.sleep(1 / tick_rate)
```

---

# 🟨 9. Integrace na straně klienta – FPS

`main_client.py`:

```python
from config.config_loader import get

FPS = get("client.fps", 60)
```

---

# 🎨 10. Budoucí první menu nastavení (náhled)

Konfigurační systém připravuje půdu pro:

* Pygame menu
* Webové admin rozhraní (skrze FastAPI)
* Ukládání vlastních presetů
* Dynamické načítání konfigurace za běhu

V dalších fázích přidáme:

* změnu stylu arény
* volbu barev týmů
* nastavení AI obtížnosti
* parametrické turnaje

---

# 🧪 11. Mini úkoly pro studenty

### 🔹 1) Přidej parametr „bounciness“

Ovlivní, jak moc se míček odráží od pálky.

### 🔹 2) Vytvoř parametr pro gravitaci míčku

Nízká, experimentální fyzika.

### 🔹 3) Přidej parametr pro zvukové efekty

Např. `sounds.enabled`.

### 🔹 4) Copilot prompt

> „Přidej validaci konfigurace v config_loader.py – pokud chybí některé klíče, vrať výchozí hodnoty a zaloguj varování.“



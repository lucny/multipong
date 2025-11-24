# **00_overview.md — Úvod do projektu MULTIPONG (Fáze 0)**

## 🎮 1. Co je MULTIPONG?

**MULTIPONG** je moderní a rozšiřitelná verze klasické hry Pong, kterou budeme společně vytvářet v Pythonu.
Projekt bude sloužit jako demonstrační platforma pro několik oblastí programování:

* **OOP (objektově orientované programování) v Pythonu**
* **Herní smyčka a grafika v Pygame**
* **Asynchronní programování pomocí asyncio**
* **Multiplayer přes WebSockety**
* **Databáze a ukládání výsledků**
* **REST API pomocí FastAPI**
* **Frontendové aplikace (web / mobil)**
* **Práce s AI nástroji (GitHub Copilot Pro)**
* **Týmová spolupráce, verzování a Git workflow**

Cílem je vytvořit **skutečnou síťovou hru**, kterou může hrát více hráčů najednou, a současně se naučit moderní postupy vývoje softwaru.

---

## 🎯 2. Hlavní cíle projektu

* vytvořit funkční hru s využitím správných principů návrhu
* naučit se rozdělit projekt do logických fází
* naučit se psát čistý, modulární a dokumentovaný kód
* naučit se spolupracovat s vývojovými nástroji, zejména Copilotem
* naučit se používat verzovací systém Git a práci s větvemi
* pochopit asynchronní běh serveru a klientů
* ukázat celý vývojový cyklus od hry → backend → databáze → API → frontend

---

## 📦 3. Jak bude projekt strukturován?

V první fázi vytvoříme základní adresářovou strukturu projektu.
Bude postupně růst, ale už nyní ji nastavíme tak, aby byla přehledná.

### Doporučená struktura projektu:

```
multipong/
│
├── docs/                 # dokumentace ke všem fázím projektu
│     ├── 00_overview.md
│     ├── 01_architecture_plan.md
│     └── … (další fáze)
│
├── multipong/            # hlavní aplikační kód
│     ├── __init__.py
│     ├── main.py         # spouštěcí soubor (zatím první verze Pygame okna)
│     ├── settings.py     # později konfigurační třídy/konstanty
│     ├── engine/         # budoucí herní engine
│     ├── network/        # budoucí WebSocket server + klient
│     ├── ui/             # budoucí Pygame render
│     └── data/           # konfigy, assets, obrázky, zvuky
│
├── tests/                # připravena pro unit testy v dalších fázích
│
├── venv/                 # virtuální prostředí (nevkládáme do Gitu)
│
├── requirements.txt      # seznam Python knihoven
└── README.md             # základní popis projektu
```

---

## 🛠 4. Co budeš potřebovat?

### Software:

* Python **3.11+**
* Pygame (`pip install pygame`)
* Git
* Editor kódu, ideálně:

  * VS Code + GitHub Copilot Pro (doporučeno)
  * PyCharm

### Kontrola instalace Pythonu:

```
python --version
```

### Vytvoření virtuálního prostředí:

```
python -m venv venv
```

### Aktivace (Windows):

```
venv\Scripts\activate
```

Linux/macOS:

```
source venv/bin/activate
```

### Instalace základních závislostí:

```
pip install pygame
```

V dalších fázích budeme instalovat:

* FastAPI
* websockets
* SQLAlchemy
* další knihovny dle potřeby

---

## 📁 5. Založení projektu krok za krokem

### 1️⃣ Vytvoř složku projektu

```
mkdir multipong
cd multipong
```

### 2️⃣ Vytvoř virtuální prostředí

```
python -m venv venv
```

### 3️⃣ Aktivuj ho a nainstaluj Pygame

```
pip install pygame
```

### 4️⃣ Vytvoř základní adresáře

```
mkdir docs multipong multipong/engine multipong/network multipong/ui multipong/data tests
```

### 5️⃣ Inicializuj Git repozitář

```
git init
```

### 6️⃣ Připrav `.gitignore`

Do souboru `.gitignore` vlož:

```
venv/
__pycache__/
*.pyc
*.log
```

### 7️⃣ Vytvoř minimální `main.py`

`multipong/main.py`:

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("MULTIPONG - Phase 0")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))
    pygame.display.flip()

pygame.quit()
```

### 8️⃣ Spusť první verzi hry

```
python multipong/main.py
```

Pokud se objeví prázdné okno 1200×800, **fáze 0 je hotová**.

---

## 🧠 6. Jak používat Copilot od Fáze 0?

Doporučené prompty:

### Prompt: *Struktura projektu*

> „Navrhni souborovou strukturu Python projektu MULTIPONG, který bude obsahovat herní engine v Pygame, WebSocket server v asyncio a pozdější FastAPI REST API.“

### Prompt: *Analyzuj kód*

> „Analyzuj tento kód a navrhni jeho reorganizaci podle principů OOP.“

### Prompt: *Přidej komentáře*

> „Přidej ke kódu stručné, věcné komentáře vhodné pro začátečníky.“

### Prompt: *Vysvětlení principů*

> „Vysvětli mi jednoduše, co dělá herní hlavní smyčka v Pygame a jak se liší od asyncio smyčky.“

---

## 🧩 7. Co bude následovat?

Po úspěšném dokončení Fáze 0 přejdeme do Fáze 1:

* vytvoříme první herní objekt (pálku)
* naučíme se vykreslovat a ovládat objekt
* ukážeme si FPS řízení a základní fyziku

Další dokument bude:

**`01_architecture_plan.md` – návrh architektury celého systému**

---

## 📘 8. Shrnutí Fáze 0

* Provedli jsme úvodní analýzu projektu MULTIPONG
* Založili jsme adresářovou strukturu
* Připravili jsme virtuální prostředí
* Spustili jsme první okno Pygame
* Připravili jsme doporučení pro práci s Copilotem
* Tím máme hotovou základní infrastrukturu celého projektu


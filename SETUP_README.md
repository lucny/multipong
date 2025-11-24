# 🚀 MULTIPONG - Setup Scripts

Tento adresář obsahuje skripty pro automatické vytvoření struktury projektu MULTIPONG.

## 📋 Dostupné skripty

### 🔷 Pro Windows (PowerShell)

**Kompletní setup (doporučeno):**
```powershell
.\setup_project.ps1
```

**Manuální kroky:**
```powershell
# 1. Pouze struktura složek a __init__.py
python create_structure.py

# 2. Placeholder moduly
python create_modules.py
```

### 🔷 Pro Linux/Mac (Bash)

**Kompletní setup (doporučeno):**
```bash
chmod +x setup_project.sh
./setup_project.sh
```

**Manuální kroky:**
```bash
# 1. Pouze struktura složek a __init__.py
python3 create_structure.py

# 2. Placeholder moduly
python3 create_modules.py
```

## 📁 Co se vytvoří?

### Struktura složek:
```
multipong/
├── multipong/
│   ├── __init__.py
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── ball.py          ✨ Třída Ball
│   │   ├── paddle.py        ✨ Třída Paddle
│   │   └── arena.py         ✨ Třída Arena
│   ├── network/
│   │   ├── __init__.py
│   │   ├── server/
│   │   │   ├── __init__.py
│   │   │   └── lobby.py     ✨ Lobby management
│   │   └── client/
│   │       ├── __init__.py
│   │       └── client.py    ✨ WebSocket klient
│   └── ai/
│       ├── __init__.py
│       └── simple_ai.py     ✨ SimpleAI
├── api/
│   ├── __init__.py
│   ├── main.py              ✨ FastAPI aplikace
│   └── routers/
│       ├── __init__.py
│       └── players.py       ✨ Players router
└── tests/
    ├── __init__.py
    ├── engine/
    │   ├── __init__.py
    │   └── test_ball.py     ✨ Testy pro Ball
    ├── network/
    │   └── __init__.py
    ├── ai/
    │   └── __init__.py
    └── api/
        └── __init__.py
```

### Vytvořené placeholder moduly:

#### 🎮 Engine (`multipong/engine/`)
- **ball.py** - Třída `Ball` s metodami `update()`, `get_position()`, `set_velocity()`
- **paddle.py** - Třída `Paddle` s metodami `move_up()`, `move_down()`, `get_rect()`
- **arena.py** - Třída `Arena` s metodami `is_out_of_bounds()`, `get_dimensions()`, `get_center()`

#### 🌐 Network Server (`multipong/network/server/`)
- **lobby.py** - Třída `Lobby` pro správu hráčů a slotů (A1-A4, B1-B4)

#### 💻 Network Client (`multipong/network/client/`)
- **client.py** - Třída `MultiPongClient` pro WebSocket komunikaci

#### 🤖 AI (`multipong/ai/`)
- **simple_ai.py** - Třída `SimpleAI` s reaktivním chováním

#### 🔌 API (`api/`)
- **main.py** - FastAPI aplikace s CORS a health check
- **routers/players.py** - Router pro správu hráčů (CRUD operace)

#### 🧪 Tests (`tests/`)
- **test_ball.py** - Základní testy pro třídu Ball

## ✅ Po spuštění setup skriptu

Po úspěšném vytvoření struktury můžete:

### 1. Nainstalovat závislosti
```bash
pip install -e .
```

### 2. Spustit testy
```bash
pytest tests/ -v
```

### 3. Spustit FastAPI server
```bash
uvicorn api.main:app --reload
```

### 4. Otevřít API dokumentaci
Otevřete v prohlížeči: http://localhost:8000/docs

## 🎯 Další kroky

Po vytvoření základní struktury:

1. ✅ Studujte vytvořené placeholder moduly
2. ✅ Rozšiřujte je podle dokumentace v `docs/`
3. ✅ Přidávejte další funkce podle fází vývoje
4. ✅ Pište testy pro nové moduly
5. ✅ Používejte GitHub Copilot podle `COPILOT_INSTRUCTIONS.md`

## 📚 Dokumentace

- **README.md** - Hlavní dokumentace projektu
- **COPILOT_INSTRUCTIONS.md** - Pravidla pro GitHub Copilot
- **CO_PILOT_GUIDE.md** - Základní návod na Copilot
- **CO_PILOT_GUIDE_ADVANCED.md** - Pokročilé techniky
- **docs/** - Detailní dokumentace všech fází vývoje

## ⚠️ Poznámky

- Všechny placeholder moduly jsou funkční a obsahují základní implementaci
- Kód respektuje PEP8 a architekturu popsanou v dokumentaci
- Můžete začít vyvíjet okamžitě po spuštění setup skriptu
- Skripty jsou idempotentní - můžete je spustit opakovaně

## 🤝 Pomoc

Pokud narazíte na problémy:

1. Zkontrolujte, že máte Python 3.9+
2. Zkontrolujte, že máte nainstalovaný pip
3. V případě PowerShell chyb: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
4. V případě bash chyb: `chmod +x setup_project.sh`

---

**Happy coding! 🎮🚀**

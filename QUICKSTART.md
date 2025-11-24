# 🎮 MULTIPONG - Rychlý start

## ⚡ Okamžité spuštění

### Windows (PowerShell):
```powershell
# Kompletní setup v jednom příkazu
.\setup_project.ps1
```

### Linux/Mac (Bash):
```bash
# Kompletní setup v jednom příkazu
chmod +x setup_project.sh
./setup_project.sh
```

## 📋 Co bylo vytvořeno?

### ✅ Struktura složek
- `multipong/engine/` - Herní engine
- `multipong/network/server/` - WebSocket server
- `multipong/network/client/` - WebSocket klient
- `multipong/ai/` - AI moduly
- `api/routers/` - FastAPI routery
- `tests/` - Testovací složky

### ✅ Placeholder moduly

| Modul | Popis | Hlavní třídy/funkce |
|-------|-------|---------------------|
| `multipong/engine/ball.py` | Míček | `Ball` - update(), get_position() |
| `multipong/engine/paddle.py` | Pálka | `Paddle` - move_up(), move_down() |
| `multipong/engine/arena.py` | Hrací plocha | `Arena` - is_out_of_bounds() |
| `multipong/network/server/lobby.py` | Lobby systém | `Lobby` - sloty A1-A4, B1-B4 |
| `multipong/network/client/client.py` | WS klient | `MultiPongClient` - connect() |
| `multipong/ai/simple_ai.py` | Reaktivní AI | `SimpleAI` - decide_action() |
| `api/main.py` | FastAPI app | app, health check |
| `api/routers/players.py` | Players API | CRUD operace |
| `tests/engine/test_ball.py` | Testy | pytest testy |

### ✅ Konfigurační soubory
- `pyproject.toml` - Moderní Python projekt config
- `requirements.txt` - Závislosti
- `.gitignore` - Git ignore
- `.env.example` - Příklad prostředí

## 🚀 Instalace a spuštění

```powershell
# 1. Instalace závislostí
pip install -e .

# 2. Spuštění testů
pytest tests/ -v

# 3. Spuštění FastAPI serveru
uvicorn api.main:app --reload

# 4. Otevřít API docs
start http://localhost:8000/docs
```

## 📚 Dokumentace

- **SETUP_README.md** - Detailní popis setup skriptů
- **README.md** - Hlavní dokumentace projektu
- **COPILOT_INSTRUCTIONS.md** - GitHub Copilot pravidla
- **docs/** - Fáze vývoje 0-14

## 🎯 Další vývoj

Projekt je připraven k vývoji podle fází v `docs/`:

1. ✅ **Fáze 0-1**: Základní struktura (HOTOVO)
2. 📝 **Fáze 2**: OOP engine rozšíření
3. 📝 **Fáze 3**: Multipong logika (4v4)
4. 📝 **Fáze 4**: Async WebSocket server
5. 📝 **Fáze 5**: Síťová synchronizace
6. 📝 ... a další podle `docs/`

---

**🎮 Začněte kódovat s pomocí GitHub Copilot!**

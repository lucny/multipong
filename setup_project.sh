#!/bin/bash

# =========================================================================
# MULTIPONG - Complete Setup Script
# Bash script pro vytvoření kompletní struktury projektu
# =========================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🎮 MULTIPONG - Setup Project Structure           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Krok 1: Vytvoření struktury složek a __init__.py
echo "📁 KROK 1: Vytváření struktury složek..."
python3 create_structure.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Chyba při vytváření struktury!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Krok 2: Vytvoření placeholder modulů
echo "🎯 KROK 2: Vytváření placeholder modulů..."
python3 create_modules.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Chyba při vytváření modulů!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Souhrn
echo "✅ HOTOVO! Struktura projektu MULTIPONG byla úspěšně vytvořena!"
echo ""
echo "📂 Struktura projektu:"
echo "  multipong/"
echo "    ├── engine/          (ball.py, paddle.py, arena.py)"
echo "    ├── network/"
echo "    │   ├── server/      (lobby.py)"
echo "    │   └── client/      (client.py)"
echo "    └── ai/              (simple_ai.py)"
echo "  api/"
echo "    ├── main.py"
echo "    └── routers/         (players.py)"
echo "  tests/"
echo "    └── engine/          (test_ball.py)"
echo ""
echo "🚀 Další kroky:"
echo "  1. Instalace závislostí:"
echo "     pip install -e ."
echo ""
echo "  2. Spuštění testů:"
echo "     pytest tests/ -v"
echo ""
echo "  3. Spuštění FastAPI serveru:"
echo "     uvicorn api.main:app --reload"
echo ""
echo "  4. Otevření API dokumentace:"
echo "     http://localhost:8000/docs"
echo ""
echo "📚 Dokumentace projektu:"
echo "  • README.md"
echo "  • COPILOT_INSTRUCTIONS.md"
echo "  • docs/"
echo ""

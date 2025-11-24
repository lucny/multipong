# =========================================================================
# MULTIPONG - Complete Setup Script
# PowerShell wrapper pro vytvoření kompletní struktury projektu
# =========================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🎮 MULTIPONG - Setup Project Structure           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Krok 1: Vytvoření struktury složek a __init__.py
Write-Host "📁 KROK 1: Vytváření struktury složek..." -ForegroundColor Yellow
python create_structure.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Chyba při vytváření struktury!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Krok 2: Vytvoření placeholder modulů
Write-Host "🎯 KROK 2: Vytváření placeholder modulů..." -ForegroundColor Yellow
python create_modules.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Chyba při vytváření modulů!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Souhrn
Write-Host "✅ HOTOVO! Struktura projektu MULTIPONG byla úspěšně vytvořena!" -ForegroundColor Green
Write-Host ""
Write-Host "📂 Struktura projektu:" -ForegroundColor Cyan
Write-Host "  multipong/" -ForegroundColor White
Write-Host "    ├── engine/          (ball.py, paddle.py, arena.py)" -ForegroundColor Gray
Write-Host "    ├── network/" -ForegroundColor White
Write-Host "    │   ├── server/      (lobby.py)" -ForegroundColor Gray
Write-Host "    │   └── client/      (client.py)" -ForegroundColor Gray
Write-Host "    └── ai/              (simple_ai.py)" -ForegroundColor Gray
Write-Host "  api/" -ForegroundColor White
Write-Host "    ├── main.py" -ForegroundColor Gray
Write-Host "    └── routers/         (players.py)" -ForegroundColor Gray
Write-Host "  tests/" -ForegroundColor White
Write-Host "    └── engine/          (test_ball.py)" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Další kroky:" -ForegroundColor Yellow
Write-Host "  1. Instalace závislostí:" -ForegroundColor White
Write-Host "     pip install -e ." -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Spuštění testů:" -ForegroundColor White
Write-Host "     pytest tests/ -v" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Spuštění FastAPI serveru:" -ForegroundColor White
Write-Host "     uvicorn api.main:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Otevření API dokumentace:" -ForegroundColor White
Write-Host "     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Dokumentace projektu:" -ForegroundColor Yellow
Write-Host "  • README.md" -ForegroundColor White
Write-Host "  • COPILOT_INSTRUCTIONS.md" -ForegroundColor White
Write-Host "  • docs/" -ForegroundColor White
Write-Host ""

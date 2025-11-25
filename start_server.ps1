# Skript pro spuštění MULTIPONG WebSocket serveru

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MULTIPONG WebSocket Server - Phase 4" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Spouštím server na http://localhost:8000" -ForegroundColor Green
Write-Host "WebSocket endpoint: ws://localhost:8000/ws/{player_id}" -ForegroundColor White
Write-Host "Test client: http://localhost:8000/test-client" -ForegroundColor White
Write-Host ""
Write-Host "Stiskni CTRL+C pro ukončení" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

& D:\projekty\multipong\.venv\Scripts\python.exe -m uvicorn multipong.network.server.websocket_server:app --host 0.0.0.0 --port 8000 --reload

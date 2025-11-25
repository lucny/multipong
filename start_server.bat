@echo off
REM Skript pro spuštění MULTIPONG WebSocket serveru

echo ============================================================
echo   MULTIPONG WebSocket Server - Phase 4
echo ============================================================
echo.
echo Spoustim server na http://localhost:8000
echo WebSocket endpoint: ws://localhost:8000/ws/{player_id}
echo Test client: http://localhost:8000/test-client
echo.
echo Stiskni CTRL+C pro ukonceni
echo ============================================================
echo.

D:\projekty\multipong\.venv\Scripts\python.exe -m uvicorn multipong.network.server.websocket_server:app --host 0.0.0.0 --port 8000 --reload

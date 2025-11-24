# **15_phase14_packaging_and_deployment.md — Build hry, deployment serveru, distribuce klienta**

## 🎯 1. Cíle fáze 14

V této fázi připravíme:

* **samostatné spouštěcí balíčky** pro Windows, macOS a Linux (PyInstaller / Briefcase)
* **Docker obraz** pro MULTIPONG server (WebSocket + FastAPI)
* **docker-compose** pro spuštění API, serveru a databáze
* **balíček klientské hry** (Pygame)
* **webhosting REST API** (uvicorn + nginx)
* **možnosti školního nasazení** (LAN verze vs. cloud)
* **bezpečnostní doporučení** (tokens, rate limiting, CORS)
* **automatizované nasazení (CI/CD)**

Fáze kombinuje praktické DevOps a moderní vývojové workflow, což je velmi vhodné pro výuku.

---

# 🧠 2. Rozdělení projektu na dvě části

MULTIPONG má dvě části:

1. **Serverová část**

   * WebSocket server (asyncio)
   * FastAPI REST API
   * databáze (SQLite nebo PostgreSQL)
   * turnajový modul

2. **Klientská část**

   * Pygame aplikace
   * frontendy (web/Flutter)

Tyto dvě části se deployují samostatně.

---

# 🧱 3. Příprava serveru pro nasazení

## 3.1 `requirements.txt`

Vytvoříme v root složce:

```
fastapi
uvicorn[standard]
sqlalchemy
asyncio
websockets
python-multipart
pydantic
```

Volitelné pro PostgreSQL:

```
psycopg2
```

## 3.2 Struktura spouštění

Ve složce `api/` máme:

* `main.py` – FastAPI
* `websocket_server.py` – multiplayer server

Připravíme orchestrátor:

`soubor: server_run.py`

```python
import asyncio
import uvicorn
from multiprocessing import Process
from multipong.network.server.websocket_server import start_websocket_server

def run_websocket():
    asyncio.run(start_websocket_server(host="0.0.0.0", port=8765))

def run_api():
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    p1 = Process(target=run_websocket)
    p2 = Process(target=run_api)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
```

---

# 🐳 4. Dockerfile pro server

`soubor: Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
EXPOSE 8765

CMD ["python", "server_run.py"]
```

---

# ⚙️ 5. docker-compose (API + Server + DB)

Doporučeno pro školní server.

`soubor: docker-compose.yml`

```yaml
version: "3.9"

services:
  multipong-db:
    image: postgres:16
    container_name: multipong-db
    restart: always
    environment:
      POSTGRES_USER: multipong
      POSTGRES_PASSWORD: password123
      POSTGRES_DB: multipong
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  multipong-server:
    build: .
    container_name: multipong-server
    restart: always
    depends_on:
      - multipong-db
    environment:
      DATABASE_URL: postgres://multipong:password123@multipong-db:5432/multipong
    ports:
      - "8000:8000"
      - "8765:8765"

volumes:
  db_data:
```

---

# 🌐 6. Nasazení FastAPI za Nginx

Pro veřejný server doporučujeme:

* uvicorn běžící na portu 8000
* nginx jako reverzní proxy na portu 80/443

Ukázka Nginx konfigurace:

`soubor: /etc/nginx/sites-available/multipong`

```nginx
server {
    listen 80;
    server_name multipong.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Pro websockety:

```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:8765;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
}
```

---

# 🧩 7. Build klienta (Pygame) pro Windows/Mac/Linux

Balíčky:

* **PyInstaller**
* nebo modernější **BeeWare Briefcase**
* nebo *portable zip* se spouštěcím skriptem

## 7.1 PyInstaller build

```
pyinstaller client_main.py --onefile --name MULTIPONG
```

Pro Windows vytvoří EXE:

```
dist/MULTIPONG.exe
```

## 7.2 macOS build

```
pyinstaller client_main.py --windowed --onefile --name MULTIPONG_MAC
```

## 7.3 Linux build

```
pyinstaller client_main.py --onefile
```

---

# 📦 8. Distribuce klienta pro studenty

Možnosti:

## A) ZIP balíček

```
MULTIPONG_client/
   MULTIPONG.exe
   assets/
   config.json
```

Studenti pouze rozbalí a spustí.

## B) Installer

InnoSetup pro Windows, DMG pro macOS.

## C) Spouštění přímo z Pythonu (ideální pro výuku)

Studenti udělají:

```
git clone multipong
pip install -r requirements_client.txt
python client_main.py
```

---

# 🔐 9. Bezpečnost nasazení

Při veřejném provozu:

✔ Zamknout CORS:

```
origins = ["https://multipong.example.com"]
```

✔ Omezit počet připojení k WS:
v managerovi:

```python
MAX_CLIENTS = 64
```

✔ Validovat zprávy klientů
(server musí chránit integritu hry)

✔ Rate limiting
maximálně 10 WS zpráv za sekundu na klienta.

✔ Oddělit API a WS pod vlastní subdomény:

```
api.multipong.cz
ws.multipong.cz
```

✔ HTTPS (Let's Encrypt)

---

# 🤖 10. Automatizace – CI/CD

Pomocí GitHub Actions:

* build Docker image
* push do GitHub Container Registry
* deploy na server (docker-compose pull + restart)

Ukázka workflow `.github/workflows/deploy.yml`:

```yaml
name: Deploy MultiPong Server

on:
  push:
    branches: ["main"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - name: Build Docker image
        run: docker build -t ghcr.io/school/multipong:latest .
      - name: Push
        run: docker push ghcr.io/school/multipong:latest
      - name: SSH deploy
        run: |
          ssh user@server "
            cd /srv/multipong &&
            docker-compose pull &&
            docker-compose up -d
          "
```

---

# 🎮 11. Deployment workflow (doporučený scénář)

Pro školní praxi:

1. **Učitel** provozuje server MULTIPONG:

   * docker-compose
   * v LAN (např. 192.168.1.10)

2. **Studenti** dostanou klienta

   * „Zadejte IP serveru“ v úvodní obrazovce

3. **Hra** probíhá celé hodiny:

   * lobby → zápasy → statistiky → turnaje

4. **REST API** poskytuje výsledky:

   * web scoreboard
   * výsledky pro rodiče
   * veřejný přehled turnajů

5. **AI trénink** probíhá mimo server (notebooky)

---

# 🧪 12. Mini úkoly pro studenty

### 🔹 1) Vytvoř instalátor pro Windows

Pomocí Inno Setup.

### 🔹 2) Vytvoř Docker image pouze pro REST API

Oddělené deploymenty.

### 🔹 3) Přidej systém verzování hry

API versioning / client version compatibility.

### 🔹 4) Copilot prompt

> „Vytvoř GitHub Actions workflow, které automaticky kompiluje Pygame klienta pomocí PyInstalleru pro Windows a přikládá ho jako artefakt release.“

---

# 📘 13. Co bude následovat?

Další obsah podle potřeb:

* **16_phase15_teacher_guide.md** – metodika výuky / jak MULTIPONG učit studenty
* **99_copilot_workflow_guide.md** – systematická práce s Copilotem v takto komplexním projektu
* **Bonus: 3D MULTIPONG** – předpoklady pro budoucí rozšíření do Unity/Three.js



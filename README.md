# 🎮 **MULTIPONG**

**Modulární výuková multiplayer hra v Pythonu**

> *Síťový Pong pro více hráčů, AI protivníky, turnajový systém a REST API.*

---

## 📌 **Obsah**

* [O projektu](#o-projektu)
* [Hlavní funkce](#hlavní-funkce)
* [Architektura](#architektura)
* [Technologie](#technologie)
* [Složky projektu](#složky-projektu)
* [Instalace a spuštění](#instalace-a-spuštění)
* [Deployment serveru](#deployment-serveru)
* [Použití Copilot Pro v tomto projektu](#použití-copilot-pro-v-tomto-projektu)
* [Vývojářská dokumentace](#vývojářská-dokumentace)
* [Plánovaný vývoj](#plánovaný-vývoj)
* [Licence](#licence)

---

# 🧠 **O projektu**

**MULTIPONG** je moderní výuková variace klasické hry Pong vytvořená pro potřeby výuky:

* objektového programování (OOP)
* práce s Git a vývojovým workflow
* multiplayer programování (WebSockety)
* REST API návrhu (FastAPI)
* databází (SQLAlchemy + SQLite/PostgreSQL)
* UI/UX (PyGame i web/Flutter klient)
* strojového učení a AI (heuristika, prediktivní model, Q-learning)
* DevOps / Deployment (Docker, docker-compose, Nginx)

Projekt je koncipován jako **dlouhodobý školní projekt**, který může být vyučován postupně, po modulech, nebo jako týmová soutěž.

---

# 🚀 **Hlavní funkce**

### 🎮 Multiplayer hra

* lokální i síťový multiplayer
* hráči se připojují k serveru přes WebSockety
* lobby systém, sloty A1–A4 a B1–B4

### 🧠 AI protivníci

* SimpleAI (reaktivní)
* PredictiveAI (odhad trajektorie míčku)
* Q-learning agent (trénovatelný v Jupyter notebooku)
* Hybridní režimy (AI doplňuje chybějící hráče)

### 📡 Síťový server

* strukturovaný WS protokol
* stavové stroje pro lobby i hru
* bezpečnostní limity proti floodu

### 📊 REST API (FastAPI)

* hráči
* zápasy
* statistiky
* leaderboard
* turnaje

### 🏆 Turnajový systém

* single elimination
* double elimination
* round robin liga
* generování pavouka
* ukládání výsledků

### 📦 Deployment

* kompletní Dockerfile
* docker-compose pro server+DB
* Nginx reverse proxy
* možnost cloud/On-prem/LAN provozu

### ✨ Výukové materiály

Projekt obsahuje obsáhlé dokumenty:

* CO_PILOT_GUIDE.md
* CO_PILOT_GUIDE_ADVANCED.md
* docs/ (všechny fáze vývoje)
* Jupyter notebook pro RL

---

# 🧱 **Architektura**

```
multipong/
│
├── engine/            # Herní jádro (míček, pálky, fyzika, aréna)
├── network/           # WebSocket server + klient
│     ├── server/
│     └── client/
├── ai/                # AI moduly (simple, predictive, q-learning)
├── api/               # FastAPI REST server + SQLAlchemy modely
├── docs/              # Dokumentace vývoje
└── notebooks/         # Jupyter RL prostředí
```

Modulární architektura zajišťuje:

* snadnou rozšiřitelnost
* přehlednost pro studenty
* paralelní vývoj více týmů

---

# 🛠️ **Technologie**

| Oblast       | Technologie                          |
| ------------ | ------------------------------------ |
| Herní klient | **PyGame**                           |
| Multiplayer  | **asyncio**, **websockets**          |
| Backend      | **FastAPI**, **uvicorn**             |
| Databáze     | **SQLAlchemy**, SQLite/PostgreSQL    |
| AI           | heuristiky, predikce, Q-learning     |
| Deployment   | Docker, docker-compose, Nginx        |
| Výuka        | GitHub Copilot Pro, Jupyter Notebook |

---

# 📁 **Složky projektu**

### 🔹 `multipong/engine/`

Herní smyčka, fyzika, třídy `Ball`, `Paddle`, `Arena`, správa skóre.

### 🔹 `multipong/network/`

Implementace WebSocket klienta i serveru.

### 🔹 `multipong/ai/`

AI strategie, Q-learning agent, prostředí pro trénink.

### 🔹 `api/`

FastAPI server, CRUD operace, SQLAlchemy modely.

### 🔹 `docs/`

Rozsáhlé vývojové dokumenty rozdělené do fází.

### 🔹 `notebooks/`

Simulační prostředí + RL trénink.

### 🔹 `COPILOT_INSTRUCTIONS.md`

Pravidla pro Copilot Pro pro celý projekt.

### 🔹 `CO_PILOT_GUIDE.md`

Základy práce s Copilotem v tomto projektu.

### 🔹 `CO_PILOT_GUIDE_ADVANCED.md`

Pokročilé techniky a architektonické prompty.

---

# ▶️ **Instalace a spuštění**

## 🐍 1. Nainstalujte Python 3.11+

## 💾 2. Nainstalujte závislosti

```
pip install -r requirements.txt
```

## ▶️ 3. Spuštění serveru

```
python server_run.py
```

Server spustí:

* WebSocket server (port 8765)
* REST API (port 8000)

## ▶️ 4. Spuštění klienta

```
python client_main.py
```

---

# 🐳 **Deployment serveru**

### 🔹 Build Docker image

```
docker build -t multipong-server .
```

### 🔹 Spuštění pomocí docker-compose

```
docker-compose up -d
```

### 🔹 Exponované porty

* `8000` — FastAPI
* `8765` — WebSocket server

---

# 🤖 **Použití Copilot Pro v tomto projektu**

Tento projekt má 3 dokumenty pro efektivní práci s Copilotem:

* **COPILOT_INSTRUCTIONS.md** – globální pravidla
* **CO_PILOT_GUIDE.md** – základní výuka
* **CO_PILOT_GUIDE_ADVANCED.md** – pokročilé techniky

Pro tvorbu nových modulů i refaktoring používejte tyto instrukce.

---

# 📚 **Vývojářská dokumentace**

Ve složce `docs/` najdete kompletní návrh i popis implementace:

* fáze 0 → příprava projektu
* fáze 1–14 → engine, AI, networking, turnaje
* jednotlivé moduly s diagramy, UML a postupy

Dále:

* RL Notebook v `notebooks/`
* diagramy REST API
* turnajová logika

---

# 📈 **Plánovaný vývoj**

* 3D MULTIPONG (Three.js / Unity / Panda3D)
* Webová aréna se záznamy zápasů
* Mobilní aplikace (Flutter)
* Pokročilý spectator mód
* Zlepšení AI (policy gradient methods, PPO)
* Automatické generování turnajů přes školní MIS

---

# 📜 **Licence**

Projekt je otevřen pro vzdělávací účely.
Možno používat, upravovat a rozšiřovat v rámci školních projektů.

---

# **09_phase8_fastapi_stats.md — REST API nad statistikami (FastAPI)**

## 🎯 1. Cíle fáze 8

V této fázi vytvoříme **REST API**, pomocí kterého bude možné zobrazovat:

* seznam hráčů
* seznam zápasů
* detail zápasu
* statistiky hráčů
* globální leaderboard
* agregované výsledky

API bude později využito:

* webovým scoreboardem
* mobilní aplikací (Flutter)
* analytickými nástroji (Jupyter Notebook)
* administrací školy

Tato vrstva odděluje **datový backend** od **uživatelských rozhraní**.

---

# 🧠 2. Proč FastAPI?

FastAPI je moderní framework s těmito výhodami:

* velmi rychlý
* generuje automaticky **Swagger UI**
* snadné psaní endpointů
* integrace s SQLAlchemy
* použitelný paralelně s WebSocket serverem

Je ideální pro výuku i produkční nasazení.

---

# 📁 3. Struktura projektu po přidání API

Rozšíříme adresář:

```
multipong/
│
├── api/
│     ├── db.py
│     ├── models.py
│     ├── crud.py
│     ├── schemas.py
│     ├── main.py
│     ├── routers/
│     │      ├── players.py
│     │      ├── matches.py
│     │      └── stats.py
│
└── multipong/
      └── ...
```

---

# 🟦 4. Pydantic schémata – `schemas.py`

Slouží k definici struktury dat, která bude API vracet.

`api/schemas.py`:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class PlayerBase(BaseModel):
    player_id: str
    name: Optional[str] = None
    team: str


class Player(PlayerBase):
    id: int
    class Config:
        orm_mode = True


class PlayerStats(BaseModel):
    player_id: int
    hits: int
    goals_scored: int
    goals_received: int

    class Config:
        orm_mode = True


class MatchBase(BaseModel):
    team_left_score: int
    team_right_score: int
    duration_seconds: int


class Match(MatchBase):
    id: int
    timestamp: datetime
    stats: List[PlayerStats] = []

    class Config:
        orm_mode = True
```

---

# 🟥 5. FAST API aplikace – `main.py`

`api/main.py`:

```python
from fastapi import FastAPI
from .routers import players, matches, stats
from .db import init_db

app = FastAPI(
    title="MULTIPONG Stats API",
    description="REST API pro hráče, zápasy a statistiky.",
    version="1.0.0"
)

# inicializace DB
init_db()

# zaregistrujeme routy
app.include_router(players.router)
app.include_router(matches.router)
app.include_router(stats.router)
```

---

# 🟧 6. Router: /players – `players.py`

`api/routers/players.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import crud, models, schemas

router = APIRouter(prefix="/players", tags=["Players"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.Player])
def list_players(db: Session = Depends(get_db)):
    return db.query(models.Player).all()

@router.get("/{player_id}", response_model=schemas.Player)
def get_player(player_id: int, db: Session = Depends(get_db)):
    return db.query(models.Player).filter(models.Player.id == player_id).first()
```

---

# 🟩 7. Router: /matches – `matches.py`

`api/routers/matches.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/matches", tags=["Matches"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.Match])
def list_matches(db: Session = Depends(get_db)):
    return db.query(models.Match).all()

@router.get("/{match_id}", response_model=schemas.Match)
def get_match(match_id: int, db: Session = Depends(get_db)):
    return db.query(models.Match).filter(models.Match.id == match_id).first()
```

---

# 🟨 8. Router: /stats – `stats.py`

Zde vytvoříme leaderboard a agregované statistiky.

`api/routers/stats.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/stats", tags=["Statistics"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db), limit: int = 10):
    return db.query(models.PlayerStats).order_by(
        models.PlayerStats.goals_scored.desc()
    ).limit(limit).all()

@router.get("/player/{player_id}")
def player_history(player_id: int, db: Session = Depends(get_db)):
    return db.query(models.PlayerStats).filter(
        models.PlayerStats.player_id == player_id
    ).all()

@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    total_matches = db.query(models.Match).count()
    total_players = db.query(models.Player).count()
    return {
        "total_matches": total_matches,
        "total_players": total_players
    }
```

---

# 🟦 9. Spuštění REST API

Z příkazové řádky:

```
uvicorn api.main:app --reload --port 9000
```

API bude dostupné na:

🔗 **[http://localhost:9000/docs](http://localhost:9000/docs)** – automatická Swagger dokumentace
🔗 **[http://localhost:9000/redoc](http://localhost:9000/redoc)** – ReDoc dokumentace

---

# 🎮 10. Testování API

### 10.1 Získání všech hráčů:

```
GET http://localhost:9000/players/
```

### 10.2 Získání leaderboardu:

```
GET http://localhost:9000/stats/leaderboard
```

### 10.3 Zápasy:

```
GET http://localhost:9000/matches/
```

---

# 🧪 11. Mini úkoly pro studenty

### 🔹 1) Seřaď leaderboard i podle „hits“

### 🔹 2) Přidej endpoint `/stats/best_defender`

Najde hráče s nejméně obdrženými góly.

### 🔹 3) Přidej endpoint `/stats/team/{team_id}`

Vrátí průměrné skóre týmu.

### 🔹 4) Copilot prompt:

> „Přidej do API endpoint /stats/winrate, který spočítá procentuální úspěšnost každého hráče“.



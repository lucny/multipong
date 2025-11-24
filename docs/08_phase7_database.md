# **08_phase7_database.md — Databázová vrstva: ukládání hráčů, zápasů a statistik**

## 🎯 1. Cíle fáze 7

V této fázi se naučíme ukládat a analyzovat výsledky hry MULTIPONG.
Databáze bude zpracovávat:

* hráče (player_id)
* výsledky zápasů
* statistiky (góly, zásahy)
* čas zápasu
* později i turnaje a leaderboardy

Tato fáze připraví základ pro REST API, webový scoreboard i analytické nástroje.

---

# 🧠 2. Proč databáze?

Chceme umět:

* zobrazovat nejlepší hráče
* archivovat odehrané zápasy
* analyzovat zásahy, góly a účast
* vytvářet frontend (web/mobil) s výsledky
* mít statistiky dostupné i po restartu hry

SQLite je ideální pro výuku – jednoduchá, bez instalace.
PostgreSQL nabídne vyšší výkon pro pozdější verzi.

---

# 🧱 3. Návrh databázových tabulek

Použijeme SQLAlchemy ORM pro práci s databází.

```
players
matches
player_stats
match_events (volitelné)
```

## 3.1 Tabulka `players`

Každý hráč = jedna pálka (A1, A2, B3…).

| Sloupec   | Typ     | Popis                 |
| --------- | ------- | --------------------- |
| id        | Integer | PK                    |
| player_id | String  | např. „A1“            |
| name      | String  | volitelné jméno hráče |
| team      | String  | „A“ nebo „B“          |

## 3.2 Tabulka `matches`

Jeden zápas MULTIPONGU.

| Sloupec          | Typ        |
| ---------------- | ---------- |
| id               | Integer PK |
| timestamp        | DateTime   |
| team_left_score  | Integer    |
| team_right_score | Integer    |
| duration_seconds | Integer    |

## 3.3 Tabulka `player_stats`

Statistika jednotlivých hráčů v daném zápase.

| Sloupec        | Typ                    |
| -------------- | ---------------------- |
| id             | Integer PK             |
| match_id       | ForeignKey(matches.id) |
| player_id      | ForeignKey(players.id) |
| hits           | Integer                |
| goals_scored   | Integer                |
| goals_received | Integer                |

---

# 📁 4. Adresářová struktura

```
multipong/
│
├── api/
│     ├── db.py
│     ├── models.py
│     ├── crud.py
│     └── ... (REST API v další fázi)
│
└── multipong/
      └── network/server/game_loop.py
```

---

# 🟦 5. Instalace SQLAlchemy

```
pip install sqlalchemy
```

Později, pokud nasadíme PostgreSQL:

```
pip install psycopg2
```

---

# 🟨 6. Soubor `db.py` – inicializace databáze

`api/db.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./multipong.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
```

Toto vytvoří *multipong.db* ve stejné složce jako API.

---

# 🟩 7. Definice modelů – `models.py`

`api/models.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    player_id = Column(String, unique=True, index=True)
    name = Column(String)
    team = Column(String)

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    team_left_score = Column(Integer)
    team_right_score = Column(Integer)
    duration_seconds = Column(Integer)

    stats = relationship("PlayerStats", back_populates="match")

class PlayerStats(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    player_id = Column(Integer, ForeignKey("players.id"))

    hits = Column(Integer)
    goals_scored = Column(Integer)
    goals_received = Column(Integer)

    match = relationship("Match", back_populates="stats")
    player = relationship("Player")
```

---

# 🟧 8. Vytvoření tabulek

V souboru `api/db.py` přidáme funkci:

```python
from .models import *

def init_db():
    Base.metadata.create_all(bind=engine)
```

Spustíme:

```
python -c "from api.db import init_db; init_db()"
```

Databáze je připravena.

---

# 🟥 9. CRUD operace – `crud.py`

Tento modul poskytuje funkce pro práci s databází.

`api/crud.py`:

```python
from sqlalchemy.orm import Session
from . import models

def create_player(db: Session, player_id: str, team: str, name: str = None):
    db_player = models.Player(player_id=player_id, team=team, name=name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def create_match(db: Session, left_score: int, right_score: int, duration: int):
    match = models.Match(team_left_score=left_score,
                         team_right_score=right_score,
                         duration_seconds=duration)
    db.add(match)
    db.commit()
    db.refresh(match)
    return match

def add_player_stats(db: Session, match_id: int, player_id: int, stats):
    db_stats = models.PlayerStats(
        match_id=match_id,
        player_id=player_id,
        hits=stats["hits"],
        goals_scored=stats["goals_scored"],
        goals_received=stats["goals_received"]
    )
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return db_stats
```

---

# 🟦 10. Napojení enginu – ukládání výsledku po zápase

Po skončení zápasu server:

1. zavolá `create_match()`
2. pro každý `PlayerStats` zavolá `add_player_stats()`

Ukázka (přidáme do game_loop po konci zápasu):

```python
from api.db import SessionLocal
from api.crud import create_match, add_player_stats

def save_match_results(engine, duration):
    db = SessionLocal()
    
    match = create_match(
        db,
        engine.team_left.score,
        engine.team_right.score,
        duration
    )

    all_paddles = engine.team_left.paddles + engine.team_right.paddles

    for p in all_paddles:
        add_player_stats(
            db, match.id,
            player_id = ... ,   # najdeme v tabulce Player
            stats = p.stats.to_dict()
        )
```

---

# 🏆 11. Leaderboard – příklad dotazu

```python
def get_leaderboard(db: Session, limit=10):
    return db.query(models.PlayerStats).order_by(
        models.PlayerStats.goals_scored.desc()
    ).limit(limit).all()
```

Později bude přístupný přes FastAPI.

---

# 🧪 12. Mini úkoly pro studenty

### 🔹 1) Přidej tabulku „match_events“

Záznam každého zásahu do míčku, včetně času a hráče.

### 🔹 2) Vytvoř dotaz:

„Kdo má nejlepší poměr hits / goals_received?“

### 🔹 3) Uprav systém hráčů:

Každý hráč má unikátní uživatelský profil a libovolně mnoho zápasů.

### 🔹 4) Copilot prompt:

> „Vytvoř SQLAlchemy dotaz, který spočítá průměrný počet zásahů míčku pro každý team v posledních 5 zápasech.“



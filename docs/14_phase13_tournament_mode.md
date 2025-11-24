# **14_phase13_tournament_mode.md — Turnaje, ligy, pavouk, žebříčky**

## 🎯 1. Cíle fáze 13

V této fázi navrhneme a implementujeme:

* **Turnajový systém** (single elimination, double elimination, round robin)
* **Ligový režim** (dlouhodobé hraní týmů i jednotlivců)
* **Generování pavouka** (automatické losování)
* **Živý žebříček hráčů** (ELO / Glicko-lite)
* **Zápis do databáze a zpětná vizualizace**
* **REST API endpointy turnajů**
* **Možné UI pro Pygame i web**

TATO fáze není povinná pro základní hru, ale posouvá MULTIPONG na úroveň plnohodnotné esportové platformy, což může být ohromující učební i motivační materiál.

---

# 🧠 2. Proč turnaje?

Turnaje umožní studentům:

* vytvářet školní soutěže
* testovat strategii **týmové spolupráce**
* sbírat data pro statistiky, grafy a AI
* soutěžit mezi třídami v rámci výuky
* naučit se návrh složitějších systémů

Pro učitele je to navíc ideální příklad:

* komplexního **workflow**
* práce s databází
* webového API
* synchronizace mezi klienty a serverem
* generování statistik (wins/losses, zápasová historie)

---

# 🧱 3. Datový model turnajů (ERD)

Přidáme 3 tabulky:

```
tournaments
tournament_matches
tournament_players  (nebo tournament_teams)
```

### 3.1 Tabulka `tournaments`

| Sloupec    | Typ      | Popis                             |
| ---------- | -------- | --------------------------------- |
| id         | PK       | identifikátor                     |
| name       | String   | název turnaje                     |
| type       | String   | "single", "double", "round_robin" |
| status     | String   | "open", "running", "finished"     |
| created_at | DateTime | datum                             |

### 3.2 Tabulka `tournament_players`

| Sloupec       | Typ      |
| ------------- | -------- |
| id            | PK       |
| tournament_id | FK       |
| player_id     | FK hráče |
| seed          | Integer  |

Možná varianta: `tournament_teams`, pokud se hraje 4v4.

### 3.3 Tabulka `tournament_matches`

| Sloupec       | Typ                                      | Popis     |
| ------------- | ---------------------------------------- | --------- |
| id            | PK                                       |           |
| tournament_id | FK                                       |           |
| match_id      | FK (odkaz na skutečný zápas v `matches`) |           |
| round         | Integer                                  | 1,2,3…    |
| slot_a        | player/team id                           | kdo hraje |
| slot_b        | player/team id                           | kdo hraje |
| winner        | id                                       | vítěz     |

---

# 🔧 4. Vytvoření modelů v SQLAlchemy

`soubor: api/models.py`

```python
class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)

    players = relationship("TournamentPlayer", back_populates="tournament")
    matches = relationship("TournamentMatch", back_populates="tournament")


class TournamentPlayer(Base):
    __tablename__ = "tournament_players"

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    seed = Column(Integer)

    tournament = relationship("Tournament", back_populates="players")
    player = relationship("Player")


class TournamentMatch(Base):
    __tablename__ = "tournament_matches"

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    round = Column(Integer)

    slot_a = Column(Integer, ForeignKey("tournament_players.id"))
    slot_b = Column(Integer, ForeignKey("tournament_players.id"))
    winner = Column(Integer, ForeignKey("tournament_players.id"), nullable=True)

    tournament = relationship("Tournament", back_populates="matches")
```

---

# 🟦 5. Typy turnajů

## 5.1 Single elimination (nejjednodušší)

Struktura:

* 8 hráčů → 4 zápasy → 2 zápasy → finále → vítěz

Losování:

```python
players = sorted(players, key=lambda p: p.seed)
bracket = list(zip(players[0::2], players[1::2]))
```

Server vytvoří autom. turnajový pavouk.

## 5.2 Double elimination

Každý hráč má druhou šanci („losers bracket“).
Je to složitější, ale výborné pro výuku.

## 5.3 Round Robin (ligová soutěž)

Každý hraje s každým.

Matice zápasů:

```
P1 vs P2
P1 vs P3
P1 vs P4
P2 vs P3
P2 vs P4
P3 vs P4
```

Celkem n(n−1)/2 zápasů.

---

# 🟧 6. REST API pro turnaje

Vytvoříme nový router:

`soubor: api/routers/tournaments.py`

## 6.1 Začátek turnaje

```http
POST /tournaments/
{
  "name": "Vánoční turnaj",
  "type": "single"
}
```

## 6.2 Přidání hráče

```http
POST /tournaments/{id}/players/
{
  "player_id": 12,
  "seed": 1
}
```

## 6.3 Generování pavouka

```http
POST /tournaments/{id}/generate_bracket
```

Server vrátí např.:

```json
{
  "rounds": [
    [
      { "match_id": null, "A": 12, "B": 8 },
      { "match_id": null, "A": 3, "B": 5 }
    ]
  ]
}
```

## 6.4 Zápis výsledku zápasu

```http
POST /tournaments/match/{id}/report
{
  "winner": 12,
  "match_id": 44   // id zápasu v 'matches'
}
```

---

# 🟩 7. Propojení s lobby

Při generování turnaje server:

* vygeneruje první dvojici (A vs B)
* otevře lobby
* hráči se připojí
* po ready → zápas proběhne
* zápas se uloží → turnajová tabulka se aktualizuje
* server vygeneruje další kolo

---

# 🎨 8. Grafika: pavouk a tabulky

Návrh vizualizace (Pygame i web):

```
Kolo 1                   Kolo 2              Finále
[Pepa] ───────┐
              ├── [Vítěz A] ────┐
[Martin] ─────┘                 ├── [Šampion]
                                │
[Kamil] ───────┐                │
              ├── [Vítěz B] ───┘
[Lukáš] ──────┘
```

Studenti mohou:

* vykreslit kostky (`pygame.draw.rect`)
* spojit je čarami
* zobrazit jména, skóre
* zvýraznit vítěze

---

# 🧮 9. ELO systém pro žebříčky

Zavedeme jednoduché ELO:

```
E_new = E_old + K * (S - P)
```

Kde:

* `S = 1` vítěz, `0` poražený
* `P` = očekávaná pravděpodobnost výhry:

```
P = 1 / (1 + 10^((E_opponent - E_self)/400))
```

Do tabulky `players` přidáme:

```
elo = Column(Integer, default=1000)
```

Po zápase:

* vítěz získá body
* poražený ztratí

Vytvoříme endpoint:

```
GET /leaderboard/elo
```

---

# 🧪 10. Mini úkoly pro studenty

### 🔹 1) Implementujte turnaj typu Round Robin

Udělejte stránku se „střihovou tabulkou“ výsledků.

### 🔹 2) Přidejte vizuální pavouk do webového frontendu

Pomocí `<svg>` elementů.

### 🔹 3) Vytvořte auto-matchmaking

Server náhodně spojuje hráče podle ELO.

### 🔹 4) Copilot prompt

> „Napiš funkci generate_double_elimination_bracket(players) a vrať strukturu horního i dolního pavouka jako JSON.“

---

# 📘 11. Shrnutí fáze

V této fázi jsme navrhli kompletní **turnajový systém**, který umožňuje:

* tvorbu turnajů
* evidenci hráčů
* generování pavouka
* řízení zápasů skrze lobby
* ukládání výsledků
* žebříčky včetně ELO

MULTIPONG se tak mění v komplexní soutěžní platformu.



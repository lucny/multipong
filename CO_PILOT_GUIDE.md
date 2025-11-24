# **CO_PILOT_GUIDE.md – Jak efektivně používat Copilot Pro v projektu MULTIPONG**

> *„Copilot není nástroj na generování kódu. Je to nástroj na **akceleraci myšlení**.“*
> — interní zásada projektu MULTIPONG

Tento dokument vás naučí používat GitHub Copilot Pro systematicky, bezpečně a efektivně při vývoji hry MULTIPONG.
Je určen studentům, učitelům i dalším vývojářům.

---

# 📘 **Obsah**

1. [Základní principy práce s Copilotem](#1-základní-principy-práce-s-copilotem)
2. [Typy Copilot interakcí (Chat, Inline, Docs)](#2-typy-copilot-interakcí)
3. [Vzory promptů pro práci v projektu MULTIPONG](#3-vzory-promptů-pro-multipong)
4. [Jak rozdělovat problém pro Copilota](#4-jak-rozkládat-problémy)
5. [Správné využití Git a branchování s Copilotem](#5-git-a-copilot)
6. [Jak žádat Copilot o refaktoring, testy a dokumentaci](#6-refaktoring-a-testy)
7. [Jak hledat chyby a ladit je pomocí Copilota](#7-debugging-s-copilotem)
8. [Architektonické prompty – engine, AI, networking, API](#8-architektonické-prompty)
9. [Anti-patterny: co po Copilotovi nikdy nechtít](#9-antipatterny)
10. [Checklist: správný Copilot prompt](#10-checklist)
11. [Přílohy a doporučení](#11-přílohy)

---

# ------------------------------------------------------------------------------

# **1. Základní principy práce s Copilotem**

Copilot není „generátor kouzelného kódu“.
Je to **asistent**, který umí:

* rychle psát boilerplate
* doplnit vaše architektonické návrhy
* vysvětlit principy
* optimalizovat kód
* navrhnout testy, refaktoring a dokumentaci
* pomoci při ladění

ALE neumí:

* řídit architekturu projektu místo vás
* zázračně odhadnout nejasné zadání
* psát kvalitní kód z vágních promptů
* číst vaše myšlenky

Nejlepší výsledky máte, když jste:

### ✔ konkrétní

### ✔ přesní

### ✔ popisujete kontext

### ✔ popisujete očekávaný formát výsledku

---

# ------------------------------------------------------------------------------

# **2. Typy Copilot interakcí**

## 🔹 2.1 Copilot Chat (globální kontext)

Vhodné pro:

* návrhy architektury
* generování modulů
* popis algoritmů
* vysvětlení principů
* hledání chyb v delších souborech

## 🔹 2.2 Inline Copilot v editoru (lokální kontext)

Vhodné pro:

* generování funkcí
* doplnění metod
* doplnění tříd
* rychlé úpravy kódu
* kontextově závislé doplňování

## 🔹 2.3 Copilot v dokumentech (Markdown, komentáře)

Vhodné pro:

* úvodní komentáře
* interní dokumentaci
* generování README / instrukcí

---

# ------------------------------------------------------------------------------

# **3. Vzory promptů pro MULTIPONG**

Níže uvádím konkrétní příklady promptů pro různé části projektu.

---

## 🎮 3.1 Herní engine (PyGame)

```
Napiš třídu Ball pro projekt MULTIPONG.
Proměnné: x, y, vx, vy, radius.
Metody: update(), draw(), reset().
Použij styl kódu odpovídající PEP8. Nepiš žádné komentáře ani vysvětlení.
```

```
Zapracuj odraz míčku od horní a dolní stěny.
Pokud narazí na zeď, invertuj vyrovnání vy.
```

---

## 🤝 3.2 Multiplayer (WebSocket server)

```
Navrhni zprávový protokol pro lobby MULTIPONG.
Události: join_lobby, choose_slot, set_ready, lobby_update, start_match.
Použij JSON. Připrav Pydantic schémata.
```

---

## 🧠 3.3 AI – Simple / Predictive / Q-learning

```
Vysvětli krok za krokem, jak vypočítat predikci dopadu míčku na osu Y
v projektu MULTIPONG. Potom navrhni metodu predict_target_y().
```

```
Napiš funkci update_Q_value() pro Q-learning.
Argumenty: Q table, state, action, reward, next_state, alpha, gamma.
```

---

## 📊 3.4 FastAPI – REST API

```
Vytvoř endpoint GET /leaderboard/elo v rámci MULTIPONG API.
Seřaď hráče podle elo hodnoty. Vrať JSON se strukturou:
[{player_id, name, elo}, ...]
```

---

## 🔧 3.5 Docker / Deployment

```
Vytvoř docker-compose.yml pro běh MULTIPONG serveru s PostgreSQL.
Porty 8000 (API) a 8765 (WS). Předpokládej obraz multipong-server:latest.
```

---

# ------------------------------------------------------------------------------

# **4. Jak rozkládat problémy, aby Copilot dobře fungoval**

Copilot miluje **hierarchické úkoly**.

### Špatně:

„Napiš hru MULTIPONG.“

### Dobře:

1. „Navrhni datové třídy pro engine.“
2. „Vytvoř jednoduchou implementaci třídy Paddle.“
3. „Doplň metodu move_up a move_down.“
4. „Vytvoř modul pro kolize.“
5. „Integruj do `MultipongEngine.update()`.“

Používej:

* **podotázky**
* **iterativní zadávání**
* **konkrétní soubory**
* **mikroúkoly**

---

# ------------------------------------------------------------------------------

# **5. Git a Copilot – správné workflow**

Nejlepší postup:

## ✔ 5.1 Každá fáze = samostatná větev

```
git checkout -b feature/ai-predictive
```

## ✔ 5.2 Používej Copilot pro commit message

```
git commit -a
```

Poté klikni na „Copilot Commit Message“.

## ✔ 5.3 Review s Copilot Chat

V editoru napiš:

```
/review
Zkontroluj tento commit a najdi možná rizika, duplicity a neefektivitu.
```

## ✔ 5.4 Merge do main až po připomínkách Copilota

---

# ------------------------------------------------------------------------------

# **6. Jak žádat Copilot o refaktoring, testy a dokumentaci**

## 🔧 6.1 Refaktoring

```
Refaktorizuj tento modul tak, aby nepoužíval duplicitu ve funkcích update().
Slouč opakující se logiku do metody handle_collision().
```

## 🧪 6.2 Automatické testy

```
Vytvoř testy PyTest pro třídu Ball.
Testy: odraz od stěny, reset, update pohybu.
```

## 📝 6.3 Dokumentace

```
Napiš Popis třídy MultipongEngine ve formátu docstringu,
vysvětli účel metod update() a render().
```

---

# ------------------------------------------------------------------------------

# **7. Debugging s Copilotem**

Když máte chybu, použijte:

```
/explain
Proč tento stacktrace vzniká? Jak tuto chybu opravit?
```

Nebo:

```
/fix
Oprav tento error. Neprováděj jiné úpravy mimo minimum potřebné pro fix.
```

Nebo:

```
/help
Co znamená tato TypeError a kde vzniká?
```

---

# ------------------------------------------------------------------------------

# **8. Architektonické prompty pro MULTIPONG**

Níže několik velmi silných promptů, které studentům velmi pomohou.

---

## 🎮 8.1 Engine struktura

```
Navrhni modulovou architekturu pro MultipongEngine.
Požaduji: Ball, Paddle, Arena, CollisionManager, ScoreManager.
Popiš komunikaci mezi třídami.
```

---

## 🌐 8.2 Lobby systém

```
Vytvoř schéma stavového stroje pro lobby multiplayer režimu MULTIPONG.
Stavy: disconnected, connecting, lobby, ready, countdown, in-game, results.
Použij PlantUML.
```

---

## 🧠 8.3 AI integrace

```
Popiš, jak propojit třídu PredictiveAI s enginem.
Napiš, jak bude engine přepisovat vstupy podle AI rozhodnutí.
```

---

## 📡 8.4 WebSocket networking

```
Navrhni kanály WS zpráv: system, lobby, game.
Popiš JSON formát zpráv game_tick a input_update.
```

---

# ------------------------------------------------------------------------------

# **9. Anti-patterny – co po Copilotovi nikdy nechtít**

❌ „Napiš komplet turnajový systém v jednom promptu.“
❌ „Napiš kompletní hru najednou.“
❌ „Oprav všechno, neřeknu co.“
❌ „Napiš AI, která hraje dokonale.“
❌ „Generuj 15 souborů v jedné odpovědi.“
❌ „Změň vše, co se ti nelíbí.“

Copilot není kouzelník.

Použij **krátké, soustředěné úkoly**.

---

# ------------------------------------------------------------------------------

# **10. Checklist kvalitního promptu**

### ✔ Kontext

Kde se kód používá, v jakém souboru?

### ✔ Cíl

Co přesně chci?

### ✔ Omezení

Bez změny existující API? Použít PEP8?

### ✔ Formát výsledku

Jen kód? Nebo i vysvětlení?

### ✔ Délka

Ne více než 1–3 odstavce zadání.

### ✔ Iterace

Po vygenerování: „Úprava verze 2“.

---

# ------------------------------------------------------------------------------

# **11. Přílohy a doporučení**

## 🧩 Doporučení pro studenty

* Před každým použitím Copilota si **napřed ujasni**, co chceš.
* Ptej se na principy, ne jen na výstupy.
* Copilot je skvělý při refaktoringu.
* Nepřebírej kód bez pochopení.
* Kombinuj Chat + Inline Copilot.
* Sleduj, co se děje v Git historii.

## 📚 Doporučený pořad výuky (teacher guide)

1. Základy promptování
2. Návrh architektury
3. Generování tříd
4. Refaktoring
5. Testování
6. Dokumentace
7. Git + Branchování
8. CI/CD pipeline
9. Deployment
10. AI moduly

---

# ------------------------------------------------------------------------------

# **Konec dokumentu**

--- IGNORE ---
Tento dokument je určen k vložení do kořenové složky projektu MULTIPONG jako **`CO_PILOT_GUIDE.md`**.
--- IGNORE ---

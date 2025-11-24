# **CO_PILOT_GUIDE_ADVANCED.md – Pokročilé techniky práce s Copilot Pro**

> *„Copilot je multiplikátor, ne náhrada vývojáře. Pokročilé techniky z vás udělají tvůrce architektury, nikoli konzumenta návrhů.“*

Tento dokument navazuje na **CO_PILOT_GUIDE.md** a zaměřuje se na:

* pokročilé prompty
* architektonické řízení Copilota
* multi-modové využití (Chat + Editor + Vnitřní kontext)
* code-reading pomocí Copilota
* deep debugging
* analýzu složitého kódu
* generování modelů, diagramů a testů
* spolupráci více studentů / týmů s Copilotem
* použití v rámci velkých projektů (120+ souborů)

---

# 📘 **Obsah**

1. [Jak pracovat s kontextem projektu (Codebase Awareness)](#1-codebase-awareness)
2. [Pokročilé prompty pro architekturu](#2-architektonické-prompty)
3. [Pokročilé prompty pro refaktoring](#3-refaktoring)
4. [Deep debugging s Copilotem](#4-deep-debugging)
5. [Jak Copilot analyzuje design patterns](#5-design-patterns)
6. [Copilot jako senior code reviewer](#6-code-reviewer)
7. [Testovací strategie: unit, integration, simulation](#7-testovací-strategie)
8. [Práce ve velkých projektech – pipeline promptů](#8-pipeline-promptů)
9. [Co je „prompt anchor“ a proč je důležitý](#9-prompt-anchor)
10. [Anti-patterny a varování](#10-antipatterny)
11. [Příklady nejúčinnějších promptů](#11-top-prompty)
12. [Závěr](#12-závěr)

---

# ------------------------------------------------------------------------------

# **1. Jak pracovat s kontextem projektu (Codebase Awareness)**

Copilot Pro má schopnost:

* číst celý projekt
* rozumět strukturovaným složkám
* reagovat na architekturu aplikace
* sledovat importy napříč moduly

Aby toho dosáhl, musíte používat:

### ✔ „Project-aware prompty“

Např.:

```
Analyzuj celý projekt MULTIPONG. Identifikuj hlavní moduly,
jejich odpovědnosti a vazby. Navrhni refaktoring stromu složek.
```

Copilot načte:

* `multipong/engine`
* `multipong/ai`
* `multipong/network`
* `api/`
* `docs/`
* `setup files`

### ✔ „Localized document prompts“

```
Vysvětli tento soubor v kontextu celého projektu:
<multipong/network/server/websocket_server.py>
Jaké má role?
```

---

# ------------------------------------------------------------------------------

# **2. Pokročilé prompty pro architekturu**

Tyto prompty prakticky *řídí celý vývoj*.

---

## 🔵 2.1 Architektura pro více modulů

```
Navrhni modulový refaktoring MULTIPONG.
Rozděl engine na subsystémy: rendering, physics, input mapping,
game state, messaging. Popiš datové toky mezi nimi.
```

---

## 🔵 2.2 Architektura pro multiplayer

```
Navrhni 3 vrstvy pro realtime multiplayer:
- authoritative server,
- client-side prediction,
- reconciliation.
Popiš minimální změny stávajícího engine MULTIPONG.
```

---

## 🔵 2.3 Architektura pro turnajový systém

```
Navrhni lifecycle turnaje: initialization, bracket_generation, match_binding,
match_execution, results_commit, next_round. Přidej diagram stavového stroje.
```

---

# ------------------------------------------------------------------------------

# **3. Pokročilé techniky refaktoringu**

## 🔧 3.1 „Refactor with constraints“

```
Refaktorizuj modul multipong/engine/engine.py tak, aby:
- žádná metoda neměla více než 30 řádků,
- kolizní logika byla v samostatné třídě,
- byla zachována kompatibilita API.
Nevytvářej nový kód mimo tento soubor.
```

---

## 🔧 3.2 Extrakce design patternu

```
Najdi části kódu v MULTIPONG, které používají implicitní Singleton,
a přepiš je tak, aby používaly explicitní DI (dependency injection).
```

---

## 🔧 3.3 „Guard rails refactoring“

Používá se pro *bezpečný refaktoring*:

```
Navrhni minimální, konzervativní refaktoring tohoto souboru:
zachovej všechny veřejné metody a jejich argumenty, refaktoruj pouze vnitřní logiku.
Vyhni se změnám signatur.
```

---

# ------------------------------------------------------------------------------

# **4. Deep debugging s Copilotem**

Copilot umí rozebrat:

* race conditions
* deadlocky
* chyby v async
* problémy se sockety
* chyby v matematice AI
* logické chyby v engine workflow

---

## 🐞 4.1 Debug race condition

```
Vyšetři, proč dochází k race condition v serveru MULTIPONG.
Kód: multipong/network/server/websocket_server.py.
Identifikuj konfliktní operace a navrhni locking nebo message buffering.
```

---

## 🐞 4.2 Debug async aplikace

```
Tento WebSocket server zamrzá po 30 minutách běhu.
Analyzuj příčiny: leakage tasků, nekonečné awaited coroutines,
absence timeoutů. Navrhni opravy.
```

---

## 🧮 4.3 Debug kolizní fyziky

```
Vysvětli, proč míček občas projde pálkou při vysoké rychlosti.
Navrhni fix pomocí swept collision detection.
```

---

# ------------------------------------------------------------------------------

# **5. Jak Copilot analyzuje design patterns**

Copilot zvládá:

* Observer pattern
* Strategy pattern (např. AI modul MULTIPONGU)
* Factory pattern
* State machine
* Dependency Injection
* ECS (Entity-Component-System)

---

## 🧩 5.1 Prompt pro návrh patternu

```
Navrhni Strategy pattern pro různé typy AI (Simple, Predictive, Q-Learning).
Vrať interface, implementace, a způsob injektování strategie do Paddle.
```

---

## 🧩 5.2 Prompt pro refaktoring na ECS

```
Přepiš návrh enginu MULTIPONG do ECS architektury.
Navrhni entity, komponenty a systémy.
Připrav diagram závislostí.
```

---

# ------------------------------------------------------------------------------

# **6. Copilot jako senior code reviewer**

Toto je *zásadní* technika.

---

## 🧐 6.1 Review:

```
/review
Proveď hluboký code review tohoto souboru.
Najdi špatné návrhy, antipatterny, technický dluh
a potenciální chyby při dlouhodobém běhu.
Navrhni konkrétní opravy.
```

---

## 🧐 6.2 Performance audit

```
Proveď performance audit enginu MULTIPONG.
Zaměř se na update(), kolizní systém a render smyčku.
Vrať seznam bottlenecků a návrh optimalizace.
```

---

## 🧐 6.3 Security audit (hlavně server)

```
Proveď bezpečnostní audit WebSocket serveru.
Hledej injection, untrusted input, překročení limitů, DoS, memory leaks.
Navrhni obranná opatření.
```

---

# ------------------------------------------------------------------------------

# **7. Testovací strategie: unit, integration, simulation**

## 🔬 7.1 Unit testy

```
Vytvoř sadu unit testů pro kolizní systém
multipong/engine/collision.py pomocí PyTestu.
```

---

## 🔬 7.2 Integration testy

```
Otestuj interakci ball-update a paddle-move přes engine.update().
Zkontroluj, že skóre se zvyšuje správně.
```

---

## 🔬 7.3 Simulation tests (AI vs AI)

```
Vytvoř test, kde dva AI hráči hrají 200 ticků proti sobě.
Na konci ověř, že míček nikdy neopustil arénu mimo branku.
```

---

# ------------------------------------------------------------------------------

# **8. Práce ve velkých projektech – pipeline promptů**

Copilot funguje nejlépe při použití „prompt pipeline“:

---

## 🟦 8.1 Fáze 1 – Analýza

```
Analyzuj modul X a shrň jeho odpovědnost, datové struktury a floaty.
```

---

## 🟩 8.2 Fáze 2 – Návrh řešení

```
Navrhni řešení pomocí dvou tříd a tří funkcí.
```

---

## 🟧 8.3 Fáze 3 – Generování implementace

```
Napiš implementaci verze 1, bez optimalizací.
```

---

## 🟥 8.4 Fáze 4 – Optimalizace

```
Optimalizuj update() tak, aby běžel v O(1) bez zbytečných podmínek.
```

---

## 🟫 8.5 Fáze 5 – Review

```
/review
Vyhodnoť kvalitu nového kódu a zkontroluj chyby.
```

---

# ------------------------------------------------------------------------------

# **9. Co je „prompt anchor“ a proč je důležitý**

„Prompt anchor“ je úvodní věta, která nastaví:

* tón
* typ odpovědi
* přesnost
* přísnost

Příklad:

```
Jsi senior Python architect se specializací na multiplayer hry.
Dodržuj PEP8. Ignoruj nejasnosti, ptej se jen na to, co je nutné.
```

Copilot se pak celé sezení drží této role.

---

# ------------------------------------------------------------------------------

# **10. Anti-patterny (pokročilá úroveň)**

❌ Generování kódu bez pochopení architektury
❌ Přepis celých modulů „na sílu“
❌ Příliš obecné prompty
❌ Ignorování návrhových vzorů
❌ Over-engineering způsobený AI
❌ Příliš mnoho odpovědnosti v jednom promptu
❌ Replikace kódu bez refaktoringu
❌ Úprava 10 souborů najednou

---

# ------------------------------------------------------------------------------

# **11. Nejlepší pokročilé prompty (TOP-Prompts)**

## 🔝 Prompt 1 – Master-level review

```
/review
Jako senior game architect: zhodnoť celý projekt MULTIPONG.
Najdi rizika, slabiny, duplicity a doporuč celkovou optimalizaci architektury.
```

---

## 🔝 Prompt 2 – Async networking excellence

```
Analyzuj potenciální deadlocky v multiplayer loopu MULTIPONG.
Navrhni návrhový pattern, který je odstraní. Použij message queue.
```

---

## 🔝 Prompt 3 – AI behaviour audit

```
Zhodnoť chování PredictiveAI. Kde jsou matematické a heuristické limity?
Navrhni realistický šum a adaptivní obtížnost.
```

---

## 🔝 Prompt 4 – Large-scale refactoring plan

```
Vytvoř detailní plán refaktoringu projektu MULTIPONG do 5 fází:
(1) architektura enginu, (2) oddělení renderu, 
(3) síťový subsystém, (4) AI modularizace, (5) test framework.
```

---

## 🔝 Prompt 5 – Deployment expert

```
Navrhni produkční nasazení MULTIPONG serveru pomocí
Docker, nginx, systemd, HTTPS a rate limiting. Přidej schematický diagram.
```

---

# ------------------------------------------------------------------------------

# **12. Závěr**

Tento dokument představuje **profesionální úroveň práce s Copilotem**, která výrazně zrychluje vývoj, ale přitom zachovává kvalitu architektury.
Studenti i učitelé by měli:

* používat Copilot jako *partnera*, ne jako „kouzelníka“
* rozkládat problémy
* iterovat
* kontrolovat výstupy
* udržovat strukturu projektu čistou a stabilní

---

Pokud chceš, mohu doplnit ještě:

* **FUNDAMENTAL_PROMPTS_AND_TEMPLATES.md**
* **TEACHER_GUIDE.md**
* **AI_WORKSHOP_GUIDE.md**
* **CO_PILOT_CODE_REVIEW_EXAMPLES.md**

Stačí říct.

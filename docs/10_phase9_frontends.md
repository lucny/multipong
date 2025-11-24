# **10_phase9_frontends.md — Webové a mobilní frontendy pro MULTIPONG**

## 🎯 1. Cíle fáze 9

V této fázi ukážeme, jak vytvořit:

* **Webový frontend** (HTML/JS nebo React)
* **Mobilní frontend** (Flutter)
* napojení na REST API (`/players`, `/matches`, `/stats`)
* jednoduchý vizuální **scoreboard**
* leaderboard zobrazující nejlepší hráče
* detail hráče s přehledem zápasů
* základy stylování a UI návrhu

Cílem není vytvořit plně dokonalou aplikaci, ale ukázat studentům moderní workflow:

> Backend → REST API → Frontend

---

# 🧠 2. Proč dělat frontend?

Umožní nám:

* vizualizovat výsledky zápasů
* vystavit leaderboard online
* nabídnout statistiky rodičům, studentům či návštěvníkům školy
* doplnit projekt do prezentovatelné podoby
* rozšířit výuku o webové technologie / mobilní vývoj

Frontend může být i soutěžní úkol — týmy připraví různé podoby UI.

---

# 📁 3. Struktura projektu – doplnění o frontendy

```
multipong/
│
├── api/                        # FastAPI REST backend
│
├── frontend_web/
│     ├── index.html
│     ├── style.css
│     └── main.js
│
└── frontend_flutter/
      └── ... (Flutter projekt)
```

---

# 🟦 4. Webový frontend – varianta 1 (ČISTÝ HTML/JS)

Nejjednodušší varianta – žádné buildování, jen statické soubory.

---

## 4.1 Soubor `index.html`

`frontend_web/index.html`:

```html
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>MULTIPONG Scoreboard</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>MULTIPONG – Scoreboard</h1>

    <section>
        <h2>Leaderboard</h2>
        <table id="leaderboard">
            <thead>
                <tr>
                    <th>Hráč</th>
                    <th>Góly</th>
                    <th>Zásahy</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </section>

    <section>
        <h2>Seznam zápasů</h2>
        <ul id="matches"></ul>
    </section>

    <script src="main.js"></script>
</body>
</html>
```

---

## 4.2 Stylování: `style.css`

Minimalisticky, ale čistě:

```css
body {
    font-family: Arial, sans-serif;
    background: #222;
    color: #eee;
    padding: 20px;
}

h1, h2 {
    color: #6cf;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}

td, th {
    border: 1px solid #555;
    padding: 10px;
}

tr:nth-child(even) {
    background: #333;
}
```

---

## 4.3 JavaScript: `main.js`

```js
const API = "http://localhost:9000";

async function fetchLeaderboard() {
    const res = await fetch(`${API}/stats/leaderboard`);
    return await res.json();
}

async function fetchMatches() {
    const res = await fetch(`${API}/matches/`);
    return await res.json();
}

function renderLeaderboard(data) {
    const tbody = document.querySelector("#leaderboard tbody");
    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.player_id}</td>
            <td>${row.goals_scored}</td>
            <td>${row.hits}</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderMatches(data) {
    const ul = document.getElementById("matches");
    ul.innerHTML = "";

    data.forEach(match => {
        const li = document.createElement("li");
        li.textContent = `Zápas #${match.id} – A: ${match.team_left_score}, B: ${match.team_right_score}`;
        ul.appendChild(li);
    });
}

async function main() {
    const leaderboard = await fetchLeaderboard();
    renderLeaderboard(leaderboard);

    const matches = await fetchMatches();
    renderMatches(matches);
}

main();
```

---

# 🟧 5. Webový frontend – varianta 2 (React)

Pro studenty, kteří chtějí moderní frontend.

## 5.1 Základní komponenty:

* `<Leaderboard />`
* `<MatchList />`
* `<PlayerDetail />`
* `<Navigation />`

Reactové komponenty lze generovat pomocí Copilota.

Př.: „Napiš React komponentu pro zobrazení leaderboardu MULTIPONG.“

---

# 🟩 6. Mobilní frontend – Flutter

Druhá volitelná varianta: **Flutter mobilní aplikace**.

---

## 6.1 Flutter GET požadavky

Ukázkový Dart kód:

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<List<dynamic>> fetchLeaderboard() async {
  final res = await http.get(Uri.parse('http://localhost:9000/stats/leaderboard'));
  return jsonDecode(res.body);
}
```

## 6.2 Jednoduchý `ListView`

```dart
import 'package:flutter/material.dart';

class LeaderboardScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("MULTIPONG Leaderboard")),
      body: FutureBuilder(
        future: fetchLeaderboard(),
        builder: (context, snap) {
          if (!snap.hasData) return Center(child: CircularProgressIndicator());

          final data = snap.data!;
          return ListView.builder(
            itemCount: data.length,
            itemBuilder: (_, i) {
              final row = data[i];
              return ListTile(
                title: Text("Hráč: ${row['player_id']}"),
                subtitle: Text("Góly: ${row['goals_scored']} — Zásahy: ${row['hits']}"),
              );
            },
          );
        },
      ),
    );
  }
}
```

---

# 🧩 7. Doporučení: rozhraní scoreboardu

Návrh pro studenty:

* nahoře:

  * logo MULTIPONG
  * volba zobrazení (Leaderboard / Hráči / Zápasy)
* uprostřed:

  * hlavní obsah (tabulka nebo seznam)
* dole:

  * podpis / info o projektu / verze API

Důraz na:

✔ čitelnost
✔ kontrast
✔ responzivitu

---

# 🧪 8. Mini úkoly pro studenty

### 🔹 1) Přidej filtr podle týmu

Leaderboard může zobrazovat jen hráče týmu A nebo B.

### 🔹 2) Doplnění grafiky

Použij Chart.js pro vykreslení grafu průběhu skóre.

### 🔹 3) Přidej stránku detailu hráče

Zobraz jeho statistiky napříč zápasy.

### 🔹 4) Copilot prompt

> „Napiš Flutter widget, který zobrazí detaily hráče z endpointu /stats/player/{id}.“

---

# 📘 9. Co bude následovat?

Další dokument:

👉 **`11_phase10_ai_bots.md` — Návrh AI hráčů, Q-learning, heuristiky a integrace do enginu.**

Ten uzavře základní architekturu MULTIPONGU a otevře prostor pro pokročilé výukové experimenty.

---

Chceš pokračovat dokumentem **11_phase10_ai_bots.md**?

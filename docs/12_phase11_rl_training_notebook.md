# **12_phase11_rl_training_notebook.md — Trénink RL agenta v Jupyter Notebooku**

## 🎯 1. Cíle fáze 11 (RL trénink)

V této fázi přeneseme myšlenku **Q-learning AI** z předchozí fáze do samostatného **tréninkového prostředí** v Jupyter Notebooku.

Naučíš se:

* vytvořit jednoduché „simulační“ prostředí MULTIPONGU pro RL (zjednodušená verze hry)
* napsat tréninkovou smyčku RL agenta (Q-learning)
* sbírat odměny a aktualizovat Q-tabuli
* ukládat naučený model na disk (např. `q_table.pkl`)
* načíst model zpět ve hře MULTIPONG jako AI hráče

Tahle fáze je ideální pro projektové práce a semináře – není nutná pro základní funkčnost hry, ale je velmi inspirativní.

---

## 🧠 2. Proč trénovat v Jupyter Notebooku?

Jupyter Notebook je vhodný pro:

* **experimentování** – měnit parametry učení a hned vidět výsledky
* **vizualizaci** – grafy průběhu odměny, konvergence, atd.
* **komentovaný kód** – vysvětlení krok za krokem
* **spolupráci s Copilotem** – krátké cell-ové prompty, rychlé úpravy

Hru MULTIPONG necháme běžet jako plnohodnotnou síťovou aplikaci, ale RL trénink si zjednodušíme do „simulačního modelu“, který běží čistě v Pythonu.

---

## 📁 3. Struktura projektu s notebookem

Doplníme složku `notebooks/`:

```
multipong/
│
├── notebooks/
│     ├── rl_training_multpong.ipynb
│
├── multipong/
│     ├── ai/
│     │     ├── qlearning_ai.py
│     │     ├── ...
│     └── engine/
│
└── docs/
      └── 12_phase11_rl_training_notebook.md
```

---

## 🧱 4. Zjednodušené „RL prostředí“ pro Pong

Pro RL nepotřebujeme celou komplexitu MULTIPONGU:

* nepotřebujeme týmy
* nepotřebujeme více pálek
* nepotřebujeme branky → stačí „odrážení“ a sledování, jestli agent trefil míček

Vytvoříme **minimalistické prostředí**:

* jeden míček
* jedna pálka (AI)
* odraz od horní a dolní stěny
* epizoda skončí, když míček proletí za pálkou

### 4.1 Třída `RLPongEnv` (v Python modulu)

Doporučené: vytvořit pomocný modul (např. `multipong/ai/rl_env.py`), který můžeme importovat v notebooku.

```python
# multipong/ai/rl_env.py

from dataclasses import dataclass

@dataclass
class State:
    ball_x: float
    ball_y: float
    ball_vx: float
    ball_vy: float
    paddle_y: float


class RLPongEnv:
    """
    Zjednodušené RL prostředí:
    - jedna pálka (vlevo)
    - míček se pohybuje doprava/doleva
    - odraz od horní/dolní stěny
    - epizoda končí, když míček proletí vlevo za pálkou
    """

    def __init__(self, width=400, height=300,
                 paddle_height=60, paddle_speed=5, ball_speed=4):
        self.width = width
        self.height = height
        self.paddle_height = paddle_height
        self.paddle_speed = paddle_speed
        self.ball_speed = ball_speed

        self.reset()

    def reset(self):
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_vx = self.ball_speed
        self.ball_vy = self.ball_speed
        self.paddle_y = self.height // 2 - self.paddle_height // 2

        return self._get_state()

    def _get_state(self):
        return State(
            ball_x=self.ball_x,
            ball_y=self.ball_y,
            ball_vx=self.ball_vx,
            ball_vy=self.ball_vy,
            paddle_y=self.paddle_y
        )

    def step(self, action):
        """
        action: 0 = nic, 1 = nahoru, 2 = dolů
        vrací: next_state, reward, done
        """

        # pohyb pálky
        if action == 1:
            self.paddle_y -= self.paddle_speed
        elif action == 2:
            self.paddle_y += self.paddle_speed

        self.paddle_y = max(0, min(self.height - self.paddle_height, self.paddle_y))

        # pohyb míčku
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        # odraz od stěn
        if self.ball_y <= 0 or self.ball_y >= self.height:
            self.ball_vy *= -1

        reward = 0
        done = False

        # kolize s pálkou (pálka je vlevo)
        if self.ball_x <= 20:  # x pozice pálky
            if self.paddle_y <= self.ball_y <= self.paddle_y + self.paddle_height:
                # zásah míčku
                self.ball_vx *= -1
                reward = 1    # odměna za zásah
            else:
                # netrefil → konec epizody
                reward = -5
                done = True

        # míček vpravo – jen odraz (aby se vracel)
        if self.ball_x >= self.width:
            self.ball_vx *= -1

        return self._get_state(), reward, done
```

---

## 📓 5. Jupyter Notebook – základní kostra

Notebook `rl_training_multpong.ipynb` může mít tyto sekce:

1. Importy a příprava prostředí
2. Diskretizace stavu
3. Q-learning smyčka
4. Vizualizace průběhu odměny
5. Uložení naučené Q-tabule
6. Krátká závěrečná evaluace

Níže je obsah, který do notebooku postupně vložíš.

---

### 5.1 Importy

```python
import numpy as np
import random
import pickle
from multipong.ai.rl_env import RLPongEnv, State
```

---

### 5.2 Diskretizace stavu

Q-learning pracuje s **diskrétním stavovým prostorem**.
Zjednodušíme:

* rozsekáme výšku obrazovky na několik „zón“
* sledujeme relativní vertikální polohu míčku vůči pálce
* sledujeme směr pohybu míčku (nahoru/dolů)

```python
def encode_state(state: State, env: RLPongEnv,
                 num_bins=10):

    # relativní pozice míčku vůči pálce
    rel_y = state.ball_y - state.paddle_y
    rel_y_norm = rel_y / env.height  # 0–1
    rel_bin = int(rel_y_norm * num_bins)
    rel_bin = max(0, min(num_bins-1, rel_bin))

    # směr pohybu míčku
    dir_y = 0 if state.ball_vy == 0 else (1 if state.ball_vy > 0 else -1)

    return (rel_bin, dir_y)
```

Akce:

```python
ACTIONS = [0, 1, 2]  # stay, up, down
```

---

### 5.3 Inicializace Q-tabule

```python
Q = {}  # Q[(state)] = np.array([Q_a0, Q_a1, Q_a2])

def get_Q(state_key):
    if state_key not in Q:
        Q[state_key] = np.zeros(len(ACTIONS))
    return Q[state_key]
```

---

### 5.4 Tréninková smyčka Q-learningu

Hyperparametry:

```python
episodes = 5000
alpha = 0.1     # learning rate
gamma = 0.95    # discount factor
epsilon = 0.1   # epsilon-greedy
env = RLPongEnv()
```

Trénink:

```python
rewards_per_episode = []

for ep in range(episodes):
    state = env.reset()
    state_key = encode_state(state, env)
    total_reward = 0

    done = False
    while not done:
        # epsilon-greedy výběr akce
        if random.random() < epsilon:
            action_idx = random.randint(0, len(ACTIONS)-1)
        else:
            q_vals = get_Q(state_key)
            action_idx = int(np.argmax(q_vals))

        action = ACTIONS[action_idx]
        next_state, reward, done = env.step(action)
        total_reward += reward

        next_state_key = encode_state(next_state, env)

        # aktualizace Q
        q_vals = get_Q(state_key)
        q_next = get_Q(next_state_key)
        q_vals[action_idx] += alpha * (reward + gamma * np.max(q_next) - q_vals[action_idx])

        state_key = next_state_key

    rewards_per_episode.append(total_reward)

    if (ep+1) % 500 == 0:
        print(f"Epizoda {ep+1}/{episodes}, průměrná odměna posledních 100: {np.mean(rewards_per_episode[-100:]):.2f}")
```

---

### 5.5 Vizualizace vývoje odměny

Pokud máš k dispozici matplotlib:

```python
import matplotlib.pyplot as plt

window = 100
smoothed = [np.mean(rewards_per_episode[max(0, i-window):i+1]) for i in range(len(rewards_per_episode))]

plt.plot(smoothed)
plt.xlabel("Epizoda")
plt.ylabel("Průměrná odměna (klouzavý průměr)")
plt.title("Učení RL agenta v RLPongEnv")
plt.show()
```

---

### 5.6 Uložení naučené Q-tabule

```python
with open("q_table_multipong.pkl", "wb") as f:
    pickle.dump(Q, f)
```

Soubor `q_table_multipong.pkl` pak zkopíruješ do např.:

```
multipong/ai/models/q_table_multipong.pkl
```

---

## 🔄 6. Načtení modelu ve hře MULTIPONG

V `QLearningAI` třídě upravíš:

```python
import pickle
from pathlib import Path

class QLearningAI(BaseAI):
    def __init__(self, table_path="multipong/ai/models/q_table_multipong.pkl",
                 epsilon=0.0):  # 0 = žádná explorace
        self.epsilon = epsilon
        self.Q = {}
        table_file = Path(table_path)
        if table_file.exists():
            with open(table_file, "rb") as f:
                self.Q = pickle.load(f)
```

A zároveň přizpůsobíš `encode_state()` v AI tak, aby používalo **stejnou logiku jako v notebooku** (stejné binování, stejná struktura klíče).

Tím získáš:

* **trénink RL agenta offline v notebooku**
* **použití naučeného chování v reálné MULTIPONG hře**

---

## 🧪 7. Mini úkoly pro studenty

1. **Změň odměnovou funkci**
   Zkus +2 za zásah, +10 za 5 zásahů za sebou, −10 za netrefení.

2. **Porovnej různé hyperparametry**
   Vyzkoušej různé kombinace α, γ, ε a zakresli, jak se mění křivka učení.

3. **Rozšíř stav**
   Přidej informaci o horizontální pozici míčku (blízko / daleko).

4. **Copilot prompt**

   > „Analyzuj tento Q-learning trénink a navrhni možnosti, jak zabránit přeučení (overfittingu) i v tomto jednoduchém prostředí.“

---

## 📘 8. Shrnutí fáze

V této fázi jsme:

* vytvořili zjednodušené RL prostředí pro Pong
* implementovali Q-learning v Jupyter Notebooku
* naučili agenta chovat se optimálněji než náhodně
* uložili naučený model
* připravili jeho integraci do reálné hry jako AI hráče

Tato fáze už překračuje běžnou středoškolskou úroveň, ale právě proto je skvělá pro talentované studenty a projektové práce.



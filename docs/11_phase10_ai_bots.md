# **11_phase10_ai_bots.md — Umělá inteligence pro MULTIPONG (AI Bots)**

## 🎯 1. Cíle fáze 10

Ve fázi 10 vytvoříme architekturu a implementace AI hráčů, kteří mohou:

* doplnit tým, když není dost lidských hráčů
* hrát proti studentovi (PvE)
* sloužit jako demonstrační modely pro výuku
* být trénováni pomocí jednoduchého RL algoritmu
* být později nahrazeni neurální sítí

Cílem je ukázat různé **úrovně obtížnosti AI**, od nejjednodušší až po adaptivní.

---

# 🧠 2. Typy AI hráčů

Navrhujeme 4 úrovně AI:

1. **LEVEL 0 – Statická AI**
   Pálka se nehýbe, vhodné pro debugging.

2. **LEVEL 1 – Heuristická AI**
   Sleduje pozici míčku a snaží se držet „střed“.

3. **LEVEL 2 – Prediktivní AI**
   Odhaduje dopad míčku podle rychlosti a úhlu.

4. **LEVEL 3 – RL Agent (Q-learning)**
   Učí se odměňováním:

   * +1 za zásah
   * +5 za gól
   * −2 za obdržený gól

Volitelné:

5. **LEVEL 4 – Neuronová síť (TensorFlow)**
   Trénovaná na záznamech zápasů.

---

# 📁 3. Struktura AI modulu

Vytvoříme novou složku:

```
multipong/
│
├── multipong/
│     ├── ai/
│     │     ├── base_ai.py
│     │     ├── simple_ai.py
│     │     ├── predictive_ai.py
│     │     ├── qlearning_ai.py
│     │     ├── nn_ai.py   (volitelné)
│     │     └── utils.py
│     └── engine/
│
└── docs/
      └── 11_phase10_ai_bots.md
```

---

# 🟦 4. Abstraktní třída AI – `base_ai.py`

Toto je základ pro všechny AI typy.

```python
class BaseAI:
    """
    Abstraktní AI hráč – poskytuje metodu 'decide'.
    Každá AI vrací dict: {"up": bool, "down": bool}
    """

    def decide(self, paddle, ball, arena):
        raise NotImplementedError
```

---

# 🟩 5. LEVEL 1 – Jednoduchá heuristická AI

### Princip:

* pokud je míček výše než pálka → jdi nahoru
* pokud je níže → jdi dolů

`soubor: ai/simple_ai.py`

```python
from .base_ai import BaseAI

class SimpleAI(BaseAI):
    def __init__(self, reaction_speed=1.0):
        self.reaction_speed = reaction_speed

    def decide(self, paddle, ball, arena):
        # jednoduché sledování míčku
        target_y = ball.y
        center = paddle.y + paddle.height / 2

        up = down = False

        if center > target_y:
            up = True
        elif center < target_y:
            down = True

        return {"up": up, "down": down}
```

---

# 🟧 6. LEVEL 2 – Prediktivní AI

Predikce místa dopadu míčku:

* lineární extrapolace trajektorie
* odraz od horní/dolní stěny
* AI se snaží být o krok napřed

`soubor: ai/predictive_ai.py`

```python
from .base_ai import BaseAI
import copy

class PredictiveAI(BaseAI):
    def __init__(self, prediction_steps=200):
        self.prediction_steps = prediction_steps

    def decide(self, paddle, ball, arena):
        # simuluj budoucí pohyb míčku
        sim = copy.copy(ball)

        for _ in range(self.prediction_steps):
            sim.update()

        target_y = sim.y
        center = paddle.y + paddle.height / 2

        return {
            "up": center > target_y,
            "down": center < target_y
        }
```

### Poznámka pro studenty:

* lze experimentovat s počtem predikčních kroků
* lze přidat šum (chyby) pro realističtější chování

---

# 🟥 7. LEVEL 3 – RL Agent (Q-learning)

Toto je výuková ukázka reinforcement learningu v jednoduché formě.

### Stav Q-learningu může obsahovat:

* relativní pozici míčku (`ball.y - paddle.y`)
* směr míčku (`sign(ball.vy)`)
* rychlost míčku (`abs(ball.vx)`)

Stav zakódujeme jako tuple:

```
state = (ball_zone, ball_direction, speed_bucket)
```

### Akce:

* 0: nic
* 1: nahoru
* 2: dolů

### Odměny:

* +1 za zásah
* +5 za gól
* –3 za obdržený gól

`soubor: ai/qlearning_ai.py`

```python
import random
from .base_ai import BaseAI

class QLearningAI(BaseAI):
    def __init__(self, lr=0.1, gamma=0.9, epsilon=0.1):
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.Q = {}  # Q[(state)][action]

    def encode_state(self, paddle, ball):
        zone = int((ball.y - paddle.y) // 30)
        direction = 1 if ball.vy > 0 else -1
        speed = int(abs(ball.vx) // 2)
        return (zone, direction, speed)

    def get_actions(self):
        return [0, 1, 2]

    def decide(self, paddle, ball, arena):
        state = self.encode_state(paddle, ball)

        # explorace vs. exploatace
        if random.random() < self.epsilon:
            action = random.choice(self.get_actions())
        else:
            Qs = self.Q.get(state, {a: 0 for a in self.get_actions()})
            action = max(Qs, key=Qs.get)

        return {
            "up": action == 1,
            "down": action == 2
        }

    def give_reward(self, paddle, ball, reward):
        state = self.encode_state(paddle, ball)
        if state not in self.Q:
            self.Q[state] = {a: 0 for a in self.get_actions()}

        best_next = max(self.Q[state].values())
        self.Q[state][self.last_action] += self.lr * (reward + self.gamma * best_next)
```

---

# 🧬 8. LEVEL 4 – Neuronová síť (TensorFlow / PyTorch)

Možnosti:

* predikce místa dopadu
* výběr akce (nahoru/dolů/nic)
* trénink na záznamech ze hry

Ukázka mini-modelu (TensorFlow):

`soubor: ai/nn_ai.py`

```python
import tensorflow as tf
from .base_ai import BaseAI

class NeuralAI(BaseAI):
    def __init__(self, model_path="model.h5"):
        self.model = tf.keras.models.load_model(model_path)

    def decide(self, paddle, ball, arena):
        features = [
            ball.x, ball.y,
            paddle.x, paddle.y,
            ball.vx, ball.vy
        ]
        inputs = tf.convert_to_tensor([features], dtype=tf.float32)
        out = self.model(inputs)[0]

        # tři hodnoty pro tři možné akce
        up, stay, down = out.numpy()

        return {
            "up": up > stay and up > down,
            "down": down > stay and down > up
        }
```

---

# 🧩 9. Integrace AI do `MultipongEngine`

Přidáme možnost, aby pálka měla přidělenou AI:

```python
paddle.ai = SimpleAI()
```

Následně v `MultipongEngine.update()`:

```python
if paddle.ai is not None:
    action = paddle.ai.decide(paddle, self.ball, self.arena)
    up = action["up"]
    down = action["down"]
else:
    # hráčské vstupy
    p_id = paddle.stats.player_id
    up = inputs.get(p_id, {}).get("up", False)
    down = inputs.get(p_id, {}).get("down", False)
```

Tento mechanismus umožňuje:

* kombinaci lidských i AI hráčů
* hru 1v4, 4v1, 4v4, 2v3 …

---

# 🎮 10. UI pro volbu AI úrovně

V menu (později):

* vybrat počet AI hráčů
* u každého napsat:

  * `Human`
  * `AI Simple`
  * `AI Predictive`
  * `AI Q-Learning`
  * `AI Neural`

Standardně:

* tým B může mít vždy alespoň 1 AI pro PvE režim
* pokud se člověk připojí přes WebSocket, AI se vypne

---

# 🧪 11. Mini úkoly pro studenty

### 🔹 1) Udělej prediktivní AI méně dokonalou

Přidej náhodný šum:
`target_y += random.uniform(-20, 20)`

### 🔹 2) Uprav Q-learning tak, aby měl „únavu“

Čím déle se hra hraje, tím více chyb dělá.

### 🔹 3) Přidej logování chování AI

Vypisování toho, proč se AI rozhodla tak či onak.

### 🔹 4) Copilot prompt

> „Vytvoř datovou strukturu pro ukládání zkušeností RL agenta (experience replay).“



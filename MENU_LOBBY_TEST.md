# 🎮 Testování Menu a Lobby systému

## ✅ Co je implementováno

- **Úvodní menu** s tlačítky (Multiplayer, Local Game, Settings, Quit)
- **Lobby UI** s výběrem slotů (A1-A4, B1-B4)
- **Countdown** před startem zápasu (3-2-1)
- **State machine** (MENU → LOBBY → COUNTDOWN → GAME)
- **WebSocket komunikace** s lobby serverem

---

## 🚀 Jak to vyzkoušet

### Varianta 1: Pouze menu (bez serveru)

```powershell
D:/projekty/multipong/.venv/Scripts/python.exe -m multipong.main_client
```

**Co uvidíš:**
- ✅ Úvodní obrazovku s tlačítky
- ✅ Můžeš klikat na tlačítka
- ⚠️ Multiplayer nebude fungovat (chybí server)

**Ovládání:**
- **ESC** - Zavřít aplikaci
- **Myš** - Klikání na tlačítka

---

### Varianta 2: S běžícím serverem (kompletní test)

#### Krok 1: Spusť server (první terminál)
```powershell
D:/projekty/multipong/.venv/Scripts/python.exe -m multipong.network.server.websocket_server
```

#### Krok 2: Spusť klienta (druhý terminál)
```powershell
D:/projekty/multipong/.venv/Scripts/python.exe -m multipong.main_client
```

**Co uvidíš:**
- ✅ Úvodní menu
- ✅ Po kliknutí na "Multiplayer" → přechod do lobby
- ✅ 8 slotů pro výběr pozice (týmy A a B)
- ✅ Ready button
- ✅ Po připojení dalších hráčů → synchronizace stavu

**Ovládání v lobby:**
- **Klik na slot** - Vybrat pozici (A1-A4 nebo B1-B4)
- **Ready button** - Označit se jako připravený
- **ESC** - Zpět do menu

#### Krok 3: Připoj další klienty (volitelné)
```powershell
D:/projekty/multipong/.venv/Scripts/python.exe -m multipong.main_client
```

Každý klient uvidí ostatní hráče v lobby.

---

## 🎯 Co testovat

### ✅ Menu
- [ ] Kliknutí na "Multiplayer" → přechod do lobby
- [ ] Kliknutí na "Local Game" → výpis v konzoli
- [ ] Kliknutí na "Settings" → výpis v konzoli
- [ ] Kliknutí na "Quit" → zavření aplikace
- [ ] ESC → zavření aplikace

### ✅ Lobby
- [ ] Zobrazení 8 slotů (A1-A4, B1-B4)
- [ ] Kliknutí na volný slot → obsazení slotu
- [ ] Barvy týmů (modrá A, červená B)
- [ ] Ready button změní stav
- [ ] ESC → zpět do menu

### ✅ WebSocket komunikace
- [ ] Po připojení → zpráva "join_lobby"
- [ ] Po výběru slotu → zpráva "choose_slot"
- [ ] Po stisknutí Ready → zpráva "set_ready"
- [ ] Příjem "lobby_update" → aktualizace UI

### ✅ Countdown
- [ ] Když všichni ready → countdown 3-2-1
- [ ] Po countdownu → přechod do hry

---

## 🐛 Známé problémy

- Server musí implementovat lobby zprávy (join_lobby, choose_slot, set_ready)
- Local game není implementováno
- Settings menu není implementováno
- Results screen není implementován

---

## 📊 Stav implementace

| Komponenta | Status | Soubor |
|-----------|--------|--------|
| MenuUI | ✅ Hotovo | `multipong/client/ui/menu.py` |
| LobbyUI | ✅ Hotovo | `multipong/client/ui/menu.py` |
| CountdownUI | ✅ Hotovo | `multipong/client/ui/menu.py` |
| State Machine | ✅ Hotovo | `multipong/main_client.py` |
| WebSocket integrace | ✅ Hotovo | `multipong/main_client.py` |
| Lobby server | ✅ Hotovo | `multipong/network/server/lobby.py` |
| Testy | ✅ 19/19 | `tests/network/test_lobby.py` |

---

## 🎓 Pro studenty

### Mini úkol 1: Přidej chat do lobby
```python
# V lobby UI přidat textové pole a seznam zpráv
# Zprávy posílat přes WebSocket: {"type": "chat", "text": "Ahoj!"}
```

### Mini úkol 2: Zobraz AI hráče jinak
```python
# V LobbyUI.draw() - když slot.is_ai == True
# Zobraz ikonu robota nebo jiné označení
```

### Mini úkol 3: Zvuky
```python
# Přidat pygame.mixer.Sound() pro:
# - Kliknutí na tlačítko
# - Výběr slotu
# - Ready stav
# - Countdown beep
```

---

## 📝 Logování

Pro debug výpisy sleduj konzoli:
```
🌐 Connecting to multiplayer server...
✓ Connected. Assigned slot: A1
🎯 Choosing slot A2
✓ Setting ready: True
🎮 Starting match!
🎮 GO! Starting game...
```

---

**Happy testing! 🎮**

"""
Skript pro vytvoření placeholder modulů MULTIPONG projektu
"""
from pathlib import Path

def create_file(filepath, content):
    """Vytvoří soubor s obsahem"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ {filepath}")

print("🎯 MULTIPONG - Vytváření placeholder modulů...\n")

# Engine moduly
print("🎮 Engine moduly...")

# ball.py
ball_content = '''"""
Ball class - Míček pro MULTIPONG engine
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Ball:
    """
    Reprezentace míčku ve hře.
    
    Attributes:
        x: X souřadnice pozice
        y: Y souřadnice pozice
        vx: Rychlost ve směru X
        vy: Rychlost ve směru Y
        radius: Poloměr míčku
    """
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 8.0
    
    def update(self, delta_time: float = 1.0) -> None:
        """Aktualizuje pozici míčku na základě rychlosti."""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
    
    def get_position(self) -> Tuple[float, float]:
        """Vrátí aktuální pozici míčku."""
        return (self.x, self.y)
    
    def set_velocity(self, vx: float, vy: float) -> None:
        """Nastaví rychlost míčku."""
        self.vx = vx
        self.vy = vy
'''

# paddle.py
paddle_content = '''"""
Paddle class - Pálka pro MULTIPONG engine
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Paddle:
    """
    Reprezentace pálky ve hře.
    
    Attributes:
        x: X souřadnice pozice
        y: Y souřadnice pozice
        width: Šířka pálky
        height: Výška pálky
        speed: Rychlost pohybu pálky
    """
    x: float
    y: float
    width: float = 10.0
    height: float = 60.0
    speed: float = 5.0
    
    def move_up(self, delta_time: float = 1.0) -> None:
        """Posune pálku nahoru."""
        self.y -= self.speed * delta_time
    
    def move_down(self, delta_time: float = 1.0) -> None:
        """Posune pálku dolů."""
        self.y += self.speed * delta_time
    
    def get_position(self) -> Tuple[float, float]:
        """Vrátí aktuální pozici pálky."""
        return (self.x, self.y)
    
    def get_rect(self) -> Tuple[float, float, float, float]:
        """Vrátí obdélník pálky (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)
'''

# arena.py
arena_content = '''"""
Arena class - Hrací plocha pro MULTIPONG engine
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Arena:
    """
    Reprezentace hrací arény.
    
    Attributes:
        width: Šířka arény
        height: Výška arény
    """
    width: int = 800
    height: int = 600
    
    def is_out_of_bounds(self, x: float, y: float) -> bool:
        """Kontroluje, zda je pozice mimo arenu."""
        return x < 0 or x > self.width or y < 0 or y > self.height
    
    def get_dimensions(self) -> Tuple[int, int]:
        """Vrátí rozměry arény."""
        return (self.width, self.height)
    
    def get_center(self) -> Tuple[float, float]:
        """Vrátí střed arény."""
        return (self.width / 2, self.height / 2)
'''

create_file("multipong/engine/ball.py", ball_content)
create_file("multipong/engine/paddle.py", paddle_content)
create_file("multipong/engine/arena.py", arena_content)

# Network Server
print("\n🌐 Network Server moduly...")

lobby_content = '''"""
Lobby management pro WebSocket server
"""

import asyncio
from typing import Dict, Set, Optional
from dataclasses import dataclass, field


@dataclass
class Player:
    """Reprezentace hráče v lobby."""
    player_id: str
    nickname: str
    slot: Optional[str] = None
    is_ready: bool = False


class Lobby:
    """
    Správa lobby pro MULTIPONG.
    Sloty: A1-A4 (tým A), B1-B4 (tým B)
    """
    
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.slots: Dict[str, Optional[str]] = {
            f"{team}{i}": None 
            for team in ['A', 'B'] 
            for i in range(1, 5)
        }
    
    async def add_player(self, player_id: str, nickname: str) -> bool:
        """Přidá hráče do lobby."""
        if player_id in self.players:
            return False
        
        self.players[player_id] = Player(
            player_id=player_id,
            nickname=nickname
        )
        return True
    
    async def assign_slot(self, player_id: str, slot: str) -> bool:
        """Přiřadí hráče do slotu."""
        if slot not in self.slots or self.slots[slot] is not None:
            return False
        
        if player_id not in self.players:
            return False
        
        self.slots[slot] = player_id
        self.players[player_id].slot = slot
        return True
    
    def get_lobby_state(self) -> dict:
        """Vrátí aktuální stav lobby."""
        return {
            "players": {
                pid: {
                    "nickname": p.nickname,
                    "slot": p.slot,
                    "ready": p.is_ready
                }
                for pid, p in self.players.items()
            },
            "slots": self.slots
        }
'''

create_file("multipong/network/server/lobby.py", lobby_content)

# Network Client
print("\n💻 Network Client moduly...")

client_content = '''"""
WebSocket klient pro připojení k MULTIPONG serveru
"""

import asyncio
import json
from typing import Optional, Callable
from websockets.asyncio.client import ClientConnection, connect


class MultiPongClient:
    """
    WebSocket klient pro MULTIPONG.
    """
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.websocket: Optional[ClientConnection] = None
        self.connected = False
        self.player_id: Optional[str] = None
    
    async def connect(self) -> bool:
        """Připojí se k serveru."""
        try:
            self.websocket = await connect(self.server_url)
            self.connected = True
            return True
        except Exception as e:
            print(f"Chyba při připojování: {e}")
            return False
    
    async def send_message(self, message_type: str, data: dict) -> None:
        """Odešle zprávu serveru."""
        if not self.websocket:
            return
        
        message = {
            "type": message_type,
            "data": data
        }
        await self.websocket.send(json.dumps(message))
    
    async def receive_message(self) -> Optional[dict]:
        """Přijme zprávu od serveru."""
        if not self.websocket:
            return None
        
        try:
            message = await self.websocket.recv()
            return json.loads(message)
        except Exception as e:
            print(f"Chyba při přijímání: {e}")
            return None
    
    async def disconnect(self) -> None:
        """Odpojí se od serveru."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
'''

create_file("multipong/network/client/client.py", client_content)

# AI moduly
print("\n🤖 AI moduly...")

simple_ai_content = '''"""
SimpleAI - Reaktivní AI pro MULTIPONG
"""

from typing import Tuple


class SimpleAI:
    """
    Jednoduchá reaktivní AI.
    Sleduje pozici míčku a pohybuje pálkou směrem k němu.
    """
    
    def __init__(self, reaction_speed: float = 0.8):
        """
        Args:
            reaction_speed: Rychlost reakce AI (0.0-1.0)
        """
        self.reaction_speed = reaction_speed
    
    def decide_action(
        self, 
        paddle_y: float, 
        ball_y: float, 
        paddle_height: float
    ) -> str:
        """
        Rozhodne o akci na základě pozice míčku.
        
        Args:
            paddle_y: Y pozice pálky
            ball_y: Y pozice míčku
            paddle_height: Výška pálky
        
        Returns:
            "up", "down", nebo "stay"
        """
        paddle_center = paddle_y + paddle_height / 2
        
        if ball_y < paddle_center - 5:
            return "up"
        elif ball_y > paddle_center + 5:
            return "down"
        else:
            return "stay"
'''

create_file("multipong/ai/simple_ai.py", simple_ai_content)

# API moduly
print("\n🔌 API moduly...")

players_router_content = '''"""
FastAPI router pro správu hráčů
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter(
    prefix="/players",
    tags=["players"]
)


class Player(BaseModel):
    """Model hráče."""
    id: Optional[int] = None
    nickname: str
    total_games: int = 0
    total_wins: int = 0
    total_losses: int = 0
    rating: int = 1000


# Dočasné úložiště (později nahradit databází)
players_db: List[Player] = []


@router.get("/", response_model=List[Player])
async def get_players():
    """Vrátí seznam všech hráčů."""
    return players_db


@router.get("/{player_id}", response_model=Player)
async def get_player(player_id: int):
    """Vrátí konkrétního hráče."""
    for player in players_db:
        if player.id == player_id:
            return player
    raise HTTPException(status_code=404, detail="Hráč nenalezen")


@router.post("/", response_model=Player)
async def create_player(player: Player):
    """Vytvoří nového hráče."""
    player.id = len(players_db) + 1
    players_db.append(player)
    return player


@router.delete("/{player_id}")
async def delete_player(player_id: int):
    """Smaže hráče."""
    for i, player in enumerate(players_db):
        if player.id == player_id:
            players_db.pop(i)
            return {"message": "Hráč smazán"}
    raise HTTPException(status_code=404, detail="Hráč nenalezen")
'''

main_api_content = '''"""
FastAPI hlavní aplikace pro MULTIPONG
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import players

app = FastAPI(
    title="MULTIPONG API",
    description="REST API pro statistiky a správu MULTIPONG hry",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrace routerů
app.include_router(players.router)


@app.get("/")
async def root():
    """Základní endpoint."""
    return {
        "message": "MULTIPONG API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
'''

create_file("api/routers/players.py", players_router_content)
create_file("api/main.py", main_api_content)

# Testy
print("\n🧪 Test moduly...")

test_ball_content = '''"""
Testy pro Ball třídu
"""

import pytest
from multipong.engine.ball import Ball


def test_ball_creation():
    """Test vytvoření míčku."""
    ball = Ball(x=100, y=100, vx=5, vy=3)
    assert ball.x == 100
    assert ball.y == 100
    assert ball.vx == 5
    assert ball.vy == 3


def test_ball_update():
    """Test aktualizace pozice míčku."""
    ball = Ball(x=0, y=0, vx=10, vy=5)
    ball.update(delta_time=1.0)
    assert ball.x == 10
    assert ball.y == 5


def test_ball_get_position():
    """Test získání pozice míčku."""
    ball = Ball(x=50, y=75, vx=0, vy=0)
    pos = ball.get_position()
    assert pos == (50, 75)
'''

create_file("tests/engine/test_ball.py", test_ball_content)

print("\n✅ Všechny placeholder moduly vytvořeny!")
print("\n📊 Vytvořené moduly:")
print("  Engine: ball.py, paddle.py, arena.py")
print("  Network Server: lobby.py")
print("  Network Client: client.py")
print("  AI: simple_ai.py")
print("  API: main.py, routers/players.py")
print("  Tests: test_ball.py")
print("\n🚀 Další kroky:")
print("  1. pip install -e .")
print("  2. pytest tests/")
print("  3. uvicorn api.main:app --reload")

"""
Skript pro vytvoření struktury MULTIPONG projektu
"""
import os
from pathlib import Path

def create_directory(path):
    """Vytvoří složku, pokud neexistuje"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"  ✓ {path}")

def create_file(filepath, content=""):
    """Vytvoří soubor s obsahem"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ {filepath}")

# Hlavní funkce
print("🎮 MULTIPONG - Vytváření struktury projektu...\n")
print("📁 Vytvářím složky...")

folders = [
    "multipong/engine",
    "multipong/network/server",
    "multipong/network/client",
    "multipong/ai",
    "api/routers",
    "tests/engine",
    "tests/network",
    "tests/ai",
    "tests/api"
]

for folder in folders:
    create_directory(folder)

print("\n📝 Vytvářím __init__.py soubory...")

# __init__.py soubory
init_files = {
    "multipong/engine/__init__.py": '''"""
Herní engine pro MULTIPONG
Obsahuje: Ball, Paddle, Arena, Physics, Collision detection
"""

__version__ = "0.1.0"
''',
    
    "multipong/network/__init__.py": '''"""
Síťová vrstva pro MULTIPONG
WebSocket server a klient pro multiplayer
"""

__version__ = "0.1.0"
''',
    
    "multipong/network/server/__init__.py": '''"""
WebSocket server pro MULTIPONG
Lobby systém, game state management, protokol komunikace
"""

__version__ = "0.1.0"
''',
    
    "multipong/network/client/__init__.py": '''"""
WebSocket klient pro MULTIPONG
Připojení k serveru, synchronizace stavu
"""

__version__ = "0.1.0"
''',
    
    "multipong/ai/__init__.py": '''"""
AI moduly pro MULTIPONG
SimpleAI, PredictiveAI, Q-Learning agent
"""

__version__ = "0.1.0"
''',
    
    "api/routers/__init__.py": '''"""
FastAPI routers pro MULTIPONG REST API
Players, matches, statistics, tournaments
"""

__version__ = "0.1.0"
''',
    
    "tests/__init__.py": "",
    "tests/engine/__init__.py": "",
    "tests/network/__init__.py": "",
    "tests/ai/__init__.py": "",
    "tests/api/__init__.py": "",
}

for filepath, content in init_files.items():
    create_file(filepath, content)

print("\n✅ Struktura složek a __init__.py soubory vytvořeny!")
print("\n🚀 Spusťte: python create_modules.py pro vytvoření placeholder modulů")

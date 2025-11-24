"""
Ukázka použití MULTIPONG Engine skeleton tříd
"""

from multipong.engine import Ball, Paddle, Arena, MultipongEngine


def demo_basic_classes():
    """Ukázka použití základních tříd."""
    print("🎮 MULTIPONG Engine Demo\n")
    print("=" * 60)
    
    # Arena
    print("\n1. Arena:")
    arena = Arena(width=1200, height=800)
    print(f"   Rozměry: {arena.get_dimensions()}")
    print(f"   Střed: {arena.get_center()}")
    print(f"   Mimo hranice (1500, 100)? {arena.is_out_of_bounds(1500, 100)}")
    
    # Ball
    print("\n2. Ball:")
    ball = Ball(x=600, y=400, vx=5, vy=3)
    print(f"   Pozice: ({ball.x}, {ball.y})")
    print(f"   Rychlost: ({ball.vx}, {ball.vy})")
    print(f"   Stav: {ball.to_dict()}")
    
    # Paddle
    print("\n3. Paddle:")
    paddle = Paddle(x=50, y=350, player_id="A1")
    print(f"   Pozice: ({paddle.x}, {paddle.y})")
    print(f"   Rozměry: {paddle.width}x{paddle.height}")
    print(f"   Player ID: {paddle.player_id}")
    print(f"   Stav: {paddle.to_dict()}")
    
    print("\n" + "=" * 60)


def demo_engine():
    """Ukázka použití MultipongEngine."""
    print("\n4. MultipongEngine:\n")
    
    # Vytvoření enginu
    engine = MultipongEngine(arena_width=1200, arena_height=800)
    print(f"   Engine vytvořen")
    print(f"   Výchozí stav: is_running={engine.is_running}")
    print(f"   Pálky: {list(engine.paddles.keys())}")
    print(f"   Skóre: {engine.score}")
    
    # Spuštění hry
    print("\n   Spouštím hru...")
    engine.start()
    print(f"   Stav po spuštění: is_running={engine.is_running}")
    
    # Získání kompletního stavu
    print("\n   Kompletní stav hry:")
    state = engine.get_state()
    
    print(f"\n   Ball pozice: ({state['ball']['x']}, {state['ball']['y']})")
    print(f"   Pálky:")
    for pid, paddle_state in state['paddles'].items():
        print(f"     - {pid}: pozice ({paddle_state['x']}, {paddle_state['y']})")
    print(f"   Skóre: Tým A: {state['score']['A']}, Tým B: {state['score']['B']}")
    print(f"   Zbývající čas: {state['time_left']}s")
    
    # Simulace vstupu
    print("\n   Simulace vstupů hráčů:")
    inputs = {
        "A1": {"up": True, "down": False},
        "B1": {"up": False, "down": True}
    }
    print(f"     A1: nahoru")
    print(f"     B1: dolů")
    engine.update(inputs)
    print(f"   ✅ Update proveden (implementace později)")
    
    # Zastavení hry
    print("\n   Zastavuji hru...")
    engine.stop()
    print(f"   Stav po zastavení: is_running={engine.is_running}")
    
    print("\n" + "=" * 60)


def demo_serialization():
    """Ukázka serializace do JSON."""
    print("\n5. JSON Serializace (pro síťovou komunikaci):\n")
    
    engine = MultipongEngine()
    import json
    
    state = engine.get_state()
    json_state = json.dumps(state, indent=2)
    
    print("   Kompletní stav jako JSON:")
    print(json_state)
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     🎮 MULTIPONG Engine - Skeleton Classes Demo          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    demo_basic_classes()
    demo_engine()
    demo_serialization()
    
    print("\n✅ Demo dokončeno!")
    print("\n📝 Další kroky:")
    print("   1. Implementovat pohybovou logiku (Ball.update, Paddle.move)")
    print("   2. Implementovat kolizní detekci")
    print("   3. Implementovat detekci gólů")
    print("   4. Připojit Pygame rendering")
    print()

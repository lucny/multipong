"""Demo MultipongEngine s více hráči (Phase 3).

Ukázka vytvoření hry s 2 hráči na tým a výpis statistik.
Spustitelné bez Pygame - čistě logický test.
"""

from multipong.engine import MultipongEngine


def main():
    print("=== MULTIPONG Phase 3 Demo ===\n")
    
    # Vytvoř engine s 2 hráči na tým
    print("Vytvářím engine s 2 hráči na tým...")
    engine = MultipongEngine(arena_width=1200, arena_height=800, num_players_per_team=2)
    engine.start()
    
    print(f"\nTým A: {len(engine.team_a.paddles)} hráčů")
    for paddle in engine.team_a.paddles:
        print(f"  - {paddle.player_id}: x={paddle.x:.0f}, zóna Y: {paddle.zone_top:.0f}-{paddle.zone_bottom:.0f}")
    
    print(f"\nTým B: {len(engine.team_b.paddles)} hráčů")
    for paddle in engine.team_b.paddles:
        print(f"  - {paddle.player_id}: x={paddle.x:.0f}, zóna Y: {paddle.zone_top:.0f}-{paddle.zone_bottom:.0f}")
    
    print(f"\nBranky:")
    print(f"  - Levá: x={engine.goal_left.x}, Y: {engine.goal_left.top}-{engine.goal_left.bottom}")
    print(f"  - Pravá: x={engine.goal_right.x}, Y: {engine.goal_right.top}-{engine.goal_right.bottom}")
    
    # Simuluj nějaké herní akce
    print("\n--- Simulace hry ---")
    
    # Simuluj zásah pálek
    print("\nSimulace zásahu míčku pálkou A1...")
    paddle_a1 = engine.team_a.paddles[0]
    engine.ball.x = paddle_a1.x + paddle_a1.width + engine.ball.radius + 1
    engine.ball.y = paddle_a1.y + paddle_a1.height / 2
    engine.ball.vx = -5
    
    engine.update({})
    print(f"Statistiky {paddle_a1.player_id}: {paddle_a1.stats.hits} zásahů")
    
    # Simuluj gól
    print("\nSimulace gólu pro tým A...")
    engine.ball.x = engine.arena.width + 10
    engine.ball.y = engine.arena.height // 2
    engine.check_score()
    
    print(f"Skóre: Tým A {engine.team_a.score} : {engine.team_b.score} Tým B")
    
    # Výpis celého stavu
    print("\n--- Kompletní stav hry ---")
    state = engine.get_state()
    
    print(f"\nMíček: x={state['ball']['x']:.1f}, y={state['ball']['y']:.1f}")
    print(f"Skóre (dict): {state['score']}")
    print(f"Tým A: {state['team_a']['score']} gólů")
    print(f"Tým B: {state['team_b']['score']} gólů")
    
    print("\nStatistiky hráčů:")
    for paddle_data in state['team_a']['paddles']:
        stats = paddle_data['stats']
        print(f"  {stats['player_id']}: {stats['hits']} zásahů, {stats['goals_scored']} gólů")
    
    for paddle_data in state['team_b']['paddles']:
        stats = paddle_data['stats']
        print(f"  {stats['player_id']}: {stats['hits']} zásahů, {stats['goals_scored']} gólů")
    
    print("\n=== Demo dokončeno ===")


if __name__ == "__main__":
    main()

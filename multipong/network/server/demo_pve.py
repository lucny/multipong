"""Demo: Student vs. AI (PvE mode) – jednoduchý příklad."""

from multipong.ai import assign_ai_to_team
from multipong.engine import MultipongEngine


def demo_pve_1v1() -> None:
    """1v1: Lidský hráč vs. jednoduchá AI."""
    print("=" * 60)
    print("DEMO: PvE (Player vs. AI) – 1v1")
    print("=" * 60)

    engine = MultipongEngine(num_players_per_team=1)

    # Tým A: lidský hráč (A1)
    # Tým B: AI (B1)
    assign_ai_to_team(engine.team_right, level=1)  # SimpleAI

    print(f"Tým A (Player):  {engine.team_left.name}")
    print(f"Tým B (SimpleAI): {engine.team_right.name}")
    print()

    engine.start()

    for tick in range(1, 61):  # 1 sekunda při 60 Hz
        # Simuluj hráče: sleduj míček pohyby nahoru/dolů
        player_input = {}
        center_y = engine.paddles["A1"].y + engine.paddles["A1"].height / 2
        if center_y > engine.ball.y:
            player_input["A1"] = {"up": True, "down": False}
        elif center_y < engine.ball.y:
            player_input["A1"] = {"up": False, "down": True}
        else:
            player_input["A1"] = {"up": False, "down": False}

        engine.update(player_input)

        if tick % 10 == 0:
            state = engine.get_state()
            print(
                f"Tick {tick}: Score A={state['score']['A']} B={state['score']['B']}, "
                f"Ball: ({state['ball']['x']:.0f}, {state['ball']['y']:.0f})"
            )

    print(f"\nKONEČNÉ SKÓRE: A={engine.score['A']} : {engine.score['B']}=B")


def demo_pve_1v3() -> None:
    """1v3: Lidský hráč vs. tři AI."""
    print("\n" + "=" * 60)
    print("DEMO: PvE (Player vs. 3x AI) – 1v3")
    print("=" * 60)

    engine = MultipongEngine(num_players_per_team=3)

    # Tým A: 1 lidský hráč (A1), ostatní AI
    assign_ai_to_team(engine.team_left, level=1)  # SimpleAI
    engine.paddles["A1"].ai = None  # Vypnutí AI pro A1 (hráč)

    # Tým B: Všichni AI
    assign_ai_to_team(engine.team_right, level=2)  # PredictiveAI

    print(f"Tým A (1 Player + 2x SimpleAI):")
    for p in engine.team_left.paddles:
        print(f"  {p.player_id}: {p.ai.__class__.__name__ if p.ai else 'Human'}")

    print(f"Tým B (3x PredictiveAI):")
    for p in engine.team_right.paddles:
        print(f"  {p.player_id}: {p.ai.__class__.__name__ if p.ai else 'Human'}")

    print()

    engine.start()

    for tick in range(1, 301):  # 5 sekund
        player_input = {}
        center_y = engine.paddles["A1"].y + engine.paddles["A1"].height / 2
        if center_y > engine.ball.y + 10:
            player_input["A1"] = {"up": True, "down": False}
        elif center_y < engine.ball.y - 10:
            player_input["A1"] = {"up": False, "down": True}
        else:
            player_input["A1"] = {"up": False, "down": False}

        engine.update(player_input)

        if tick % 60 == 0:
            state = engine.get_state()
            print(
                f"Tick {tick}: Score A={state['score']['A']} B={state['score']['B']}, "
                f"Rally hits: {state['rally_hits']}"
            )

    print(f"\nKONEČNÉ SKÓRE: A={engine.score['A']} : {engine.score['B']}=B")


if __name__ == "__main__":
    demo_pve_1v1()
    demo_pve_1v3()

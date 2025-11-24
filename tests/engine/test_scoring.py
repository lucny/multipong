"""Testy skórování, resetování a zrychlování míčku."""
from multipong.engine.game_engine import MultipongEngine
from multipong import settings


def test_ball_speed_increases_after_paddle_collision():
    """Rychlost míčku se po odrazu od pálky zvýší."""
    engine = MultipongEngine()
    engine.start()
    left = engine.paddles["A1"]
    
    # Nastav míček těsně vpravo od pálky
    engine.ball.x = left.x + left.width + engine.ball.radius + 1
    engine.ball.y = left.y + left.height / 2
    engine.ball.vx = -5.0
    engine.ball.vy = 3.0
    
    initial_vx = abs(engine.ball.vx)
    initial_vy = abs(engine.ball.vy)
    
    engine.update({})
    
    # Po odrazu by rychlost měla vzrůst
    assert abs(engine.ball.vx) > initial_vx, "Vx by se měl zvýšit po odrazu."
    assert abs(engine.ball.vy) > initial_vy, "Vy by se měl zvýšit po odrazu."


def test_goal_detection_left_side():
    """Míček proletí levou hranou -> gól pro tým B."""
    engine = MultipongEngine()
    engine.ball.x = 5
    engine.ball.y = 400
    
    scoring = engine.check_goals()
    assert scoring == "B", "Gól přes levou hranici znamená bod pro B."


def test_goal_detection_right_side():
    """Míček proletí pravou hranou -> gól pro tým A."""
    engine = MultipongEngine()
    engine.ball.x = engine.arena.width - 5
    engine.ball.y = 400
    
    scoring = engine.check_goals()
    assert scoring == "A", "Gól přes pravou hranici znamená bod pro A."


def test_score_increments_on_goal():
    """Po gólu se skóre zvýší a míček se resetuje."""
    engine = MultipongEngine()
    initial_a = engine.score["A"]
    initial_b = engine.score["B"]
    
    # Simuluj gól pro A
    engine.ball.x = engine.arena.width + 10
    engine.check_score()
    
    assert engine.score["A"] == initial_a + 1, "Skóre A by mělo vzrůst."
    # Míček by měl být zpět na středu
    cx, _ = engine.arena.get_center()
    assert abs(engine.ball.x - cx) < 10, "Míček by měl být po gólu resetován do středu."


def test_reset_method_clears_score_and_positions():
    """Metoda reset() vrátí skóre na 0 a pálky na střed."""
    engine = MultipongEngine()
    engine.score["A"] = 5
    engine.score["B"] = 3
    engine.ball.x = 100
    engine.paddles["A1"].y = 50
    
    engine.reset()
    
    assert engine.score["A"] == 0
    assert engine.score["B"] == 0
    cx, cy = engine.arena.get_center()
    assert abs(engine.ball.x - cx) < 1
    assert abs(engine.ball.y - cy) < 1
    # Pálky by měly být na střední výšce
    center_y = engine.arena.height / 2
    left_expected = center_y - engine.paddles["A1"].height / 2
    assert abs(engine.paddles["A1"].y - left_expected) < 1


def test_reset_ball_restores_initial_speed():
    """reset_ball() obnoví původní rychlost (bez zrychlení)."""
    engine = MultipongEngine()
    engine.ball.vx = 12.0  # Uměle navýšeno
    engine.ball.vy = -8.0
    
    engine.reset_ball()
    
    # Rychlost by měla být zpět na základní hodnotu (se zachováním směru)
    assert abs(abs(engine.ball.vx) - settings.BALL_SPEED_X) < 0.1
    assert abs(abs(engine.ball.vy) - settings.BALL_SPEED_Y) < 0.1

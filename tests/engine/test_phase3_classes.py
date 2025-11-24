"""Testy pro PlayerStats, Team a GoalZone."""

from multipong.engine.player_stats import PlayerStats
from multipong.engine.team import Team
from multipong.engine.goal_zone import GoalZone
from multipong.engine.paddle import Paddle
from multipong.engine.ball import Ball


class TestPlayerStats:
    """Testy pro PlayerStats."""
    
    def test_player_stats_creation(self):
        """Test vytvoření statistik hráče."""
        stats = PlayerStats("A1")
        assert stats.player_id == "A1"
        assert stats.hits == 0
        assert stats.goals_scored == 0
        assert stats.goals_received == 0
    
    def test_record_hit(self):
        """Test zaznamenání zásahu."""
        stats = PlayerStats("A1")
        stats.record_hit()
        stats.record_hit()
        assert stats.hits == 2
    
    def test_record_goal_scored(self):
        """Test zaznamenání vstřeleného gólu."""
        stats = PlayerStats("A1")
        stats.record_goal_scored()
        assert stats.goals_scored == 1
    
    def test_record_goal_received(self):
        """Test zaznamenání obdrženého gólu."""
        stats = PlayerStats("A1")
        stats.record_goal_received()
        assert stats.goals_received == 1
    
    def test_to_dict(self):
        """Test serializace do slovníku."""
        stats = PlayerStats("B2")
        stats.hits = 5
        stats.goals_scored = 2
        stats.goals_received = 1
        
        data = stats.to_dict()
        assert data["player_id"] == "B2"
        assert data["hits"] == 5
        assert data["goals_scored"] == 2
        assert data["goals_received"] == 1
    
    def test_reset(self):
        """Test resetování statistik."""
        stats = PlayerStats("A1")
        stats.hits = 10
        stats.goals_scored = 3
        stats.goals_received = 2
        
        stats.reset()
        assert stats.hits == 0
        assert stats.goals_scored == 0
        assert stats.goals_received == 0


class TestTeam:
    """Testy pro Team."""
    
    def test_team_creation(self):
        """Test vytvoření týmu."""
        paddle1 = Paddle(50, 100, player_id="A1")
        paddle2 = Paddle(150, 100, player_id="A2")
        team = Team("A", [paddle1, paddle2])
        
        assert team.name == "A"
        assert len(team.paddles) == 2
        assert team.score == 0
    
    def test_add_score(self):
        """Test přičtení gólu."""
        paddle = Paddle(50, 100, player_id="A1")
        team = Team("A", [paddle])
        
        team.add_score()
        assert team.score == 1
        # Kontrola že se zaznamenalo i do statistik hráče
        assert paddle.stats.goals_scored == 1
    
    def test_reset_score(self):
        """Test resetování skóre."""
        paddle = Paddle(50, 100, player_id="A1")
        team = Team("A", [paddle])
        team.score = 5
        
        team.reset_score()
        assert team.score == 0
    
    def test_to_dict(self):
        """Test serializace týmu."""
        paddle = Paddle(50, 100, player_id="A1")
        paddle.stats.hits = 3
        team = Team("A", [paddle])
        team.score = 2
        
        data = team.to_dict()
        assert data["name"] == "A"
        assert data["score"] == 2
        assert len(data["paddles"]) == 1
        assert data["paddles"][0]["stats"]["player_id"] == "A1"
        assert data["paddles"][0]["stats"]["hits"] == 3


class TestGoalZone:
    """Testy pro GoalZone."""
    
    def test_goal_zone_creation(self):
        """Test vytvoření branky."""
        goal = GoalZone(x=0, top=100, bottom=300)
        assert goal.x == 0
        assert goal.top == 100
        assert goal.bottom == 300
    
    def test_check_goal_left_success(self):
        """Test detekce gólu vlevo (míček proletěl)."""
        goal = GoalZone(x=0, top=200, bottom=400)
        ball = Ball(5, 300, radius=10)  # Míček blízko levé hranice
        
        assert goal.check_goal(ball) is True
    
    def test_check_goal_left_miss_vertical(self):
        """Test detekce gólu vlevo - míč mimo vertikální rozsah."""
        goal = GoalZone(x=0, top=200, bottom=400)
        ball = Ball(5, 500, radius=10)  # Mimo rozsah branky
        
        assert goal.check_goal(ball) is False
    
    def test_check_goal_right_success(self):
        """Test detekce gólu vpravo."""
        goal = GoalZone(x=1200, top=200, bottom=400)
        ball = Ball(1195, 300, radius=10)  # Blízko pravé hranice
        
        assert goal.check_goal(ball) is True
    
    def test_check_goal_not_reached(self):
        """Test když míček není u branky."""
        goal = GoalZone(x=0, top=200, bottom=400)
        ball = Ball(600, 300, radius=10)  # Uprostřed hřiště
        
        assert goal.check_goal(ball) is False
    
    def test_to_dict(self):
        """Test serializace branky."""
        goal = GoalZone(x=1200, top=150, bottom=450)
        data = goal.to_dict()
        
        assert data["x"] == 1200
        assert data["top"] == 150
        assert data["bottom"] == 450


class TestMultipongEngineWithTeams:
    """Testy pro MultipongEngine s Team architekturou."""
    
    def test_engine_creates_teams(self):
        """Test že engine vytvoří oba týmy."""
        from multipong.engine import MultipongEngine
        engine = MultipongEngine()
        
        assert engine.team_a is not None
        assert engine.team_b is not None
        assert engine.team_a.name == "A"
        assert engine.team_b.name == "B"
    
    def test_engine_multiple_players_per_team(self):
        """Test vytvoření enginu s více hráči na tým."""
        from multipong.engine import MultipongEngine
        engine = MultipongEngine(num_players_per_team=2)
        
        assert len(engine.team_a.paddles) == 2
        assert len(engine.team_b.paddles) == 2
        assert "A1" in engine.paddles
        assert "A2" in engine.paddles
        assert "B1" in engine.paddles
        assert "B2" in engine.paddles
    
    def test_paddle_zones_assigned(self):
        """Test že pálky mají přiřazené zóny."""
        from multipong.engine import MultipongEngine
        engine = MultipongEngine(arena_height=800, num_players_per_team=4)
        
        # Každá pálka má zónu 200px vysokou (800/4)
        for paddle in engine.team_a.paddles:
            assert paddle.zone_top is not None
            assert paddle.zone_bottom is not None
            assert paddle.zone_bottom - paddle.zone_top == 200
    
    def test_goal_zones_created(self):
        """Test že branky jsou vytvořeny."""
        from multipong.engine import MultipongEngine
        engine = MultipongEngine()
        
        assert engine.goal_left is not None
        assert engine.goal_right is not None
        assert engine.goal_left.x == 0
        assert engine.goal_right.x == engine.arena.width
    
    def test_goal_increments_team_score(self):
        """Test že gól zvýší skóre týmu."""
        from multipong.engine import MultipongEngine
        engine = MultipongEngine()
        
        # Simuluj gól pro tým A (míček vpravo)
        engine.ball.x = engine.arena.width + 10
        engine.ball.y = engine.arena.height // 2
        engine.check_score()
        
        assert engine.team_a.score == 1
        assert engine.score["A"] == 1  # Zpětná kompatibilita
    
    def test_paddle_hit_records_stats(self):
        """Test že zásah pálkou zaznamená statistiku."""
        from multipong.engine import MultipongEngine
        engine = MultipongEngine()
        engine.start()
        
        paddle = engine.team_a.paddles[0]
        initial_hits = paddle.stats.hits
        
        # Nastav míček na kolizi
        engine.ball.x = paddle.x + paddle.width + engine.ball.radius + 1
        engine.ball.y = paddle.y + paddle.height / 2
        engine.ball.vx = -5
        
        engine.update({})
        
        assert paddle.stats.hits == initial_hits + 1

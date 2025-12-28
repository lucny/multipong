"""
Testy pro databázové CRUD operace.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db import Base
from api import models, crud


# Použijeme in-memory SQLite databázi pro testy
@pytest.fixture
def test_db():
    """Vytvoří dočasnou in-memory databázi pro testy."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


class TestPlayerCrud:
    """Testy pro operace s hráči."""
    
    def test_create_player(self, test_db):
        """Test vytvoření hráče."""
        player = crud.create_player(test_db, "A1", "A", "Alice")
        
        assert player.player_id == "A1"
        assert player.team == "A"
        assert player.name == "Alice"
        assert player.id is not None
    
    def test_get_player(self, test_db):
        """Test získání hráče."""
        crud.create_player(test_db, "B2", "B", "Bob")
        player = crud.get_player(test_db, "B2")
        
        assert player is not None
        assert player.player_id == "B2"
        assert player.team == "B"
    
    def test_get_nonexistent_player(self, test_db):
        """Test získání neexistujícího hráče."""
        player = crud.get_player(test_db, "X9")
        assert player is None
    
    def test_get_or_create_player(self, test_db):
        """Test get_or_create (vytvoří pokud neexistuje)."""
        # První call - vytvoří
        player1 = crud.get_or_create_player(test_db, "A3", "A")
        assert player1.player_id == "A3"
        player1_id = player1.id
        
        # Druhý call - vybere existujícího
        player2 = crud.get_or_create_player(test_db, "A3", "A")
        assert player2.id == player1_id
    
    def test_get_all_players(self, test_db):
        """Test získání všech hráčů."""
        crud.create_player(test_db, "A1", "A")
        crud.create_player(test_db, "B1", "B")
        
        players = crud.get_all_players(test_db)
        assert len(players) == 2
    
    def test_delete_player(self, test_db):
        """Test smazání hráče."""
        crud.create_player(test_db, "A1", "A")
        assert crud.get_player(test_db, "A1") is not None
        
        result = crud.delete_player(test_db, "A1")
        assert result is True
        assert crud.get_player(test_db, "A1") is None


class TestMatchCrud:
    """Testy pro operace se zápasy."""
    
    def test_create_match(self, test_db):
        """Test vytvoření zápasu."""
        match = crud.create_match(test_db, team_left_score=3, team_right_score=2, duration_seconds=120)
        
        assert match.team_left_score == 3
        assert match.team_right_score == 2
        assert match.duration_seconds == 120
        assert match.id is not None
    
    def test_get_match(self, test_db):
        """Test získání zápasu."""
        match1 = crud.create_match(test_db, 5, 4, 180)
        match2 = crud.get_match(test_db, match1.id)
        
        assert match2 is not None
        assert match2.team_left_score == 5
        assert match2.team_right_score == 4
    
    def test_get_all_matches(self, test_db):
        """Test získání všech zápasů."""
        crud.create_match(test_db, 1, 0, 60)
        crud.create_match(test_db, 2, 1, 90)
        
        matches = crud.get_all_matches(test_db)
        assert len(matches) == 2
    
    def test_get_all_matches_with_limit(self, test_db):
        """Test získání zápasů s limitem."""
        crud.create_match(test_db, 1, 0, 60)
        crud.create_match(test_db, 2, 1, 90)
        crud.create_match(test_db, 3, 2, 120)
        
        matches = crud.get_all_matches(test_db, limit=2)
        assert len(matches) == 2


class TestPlayerStatsCrud:
    """Testy pro operace s statistikami."""
    
    def test_add_player_stats(self, test_db):
        """Test přidání statistiky hráče."""
        # Vytvoříme hráče a zápas
        crud.create_player(test_db, "A1", "A")
        match = crud.create_match(test_db, 2, 1, 90)
        
        # Přidáme statistiku
        stats = crud.add_player_stats(
            test_db,
            match_id=match.id,
            player_id="A1",
            hits=15,
            goals_scored=2,
            goals_received=1
        )
        
        assert stats is not None
        assert stats.hits == 15
        assert stats.goals_scored == 2
        assert stats.goals_received == 1
    
    def test_add_stats_nonexistent_player(self, test_db):
        """Test přidání statistiky pro neexistujícího hráče."""
        match = crud.create_match(test_db, 1, 0, 60)
        
        stats = crud.add_player_stats(
            test_db, match.id, "X9", 10, 1, 0
        )
        
        assert stats is None
    
    def test_get_player_stats(self, test_db):
        """Test získání statistik hráče."""
        crud.create_player(test_db, "B1", "B")
        match1 = crud.create_match(test_db, 2, 1, 90)
        match2 = crud.create_match(test_db, 3, 2, 120)
        
        crud.add_player_stats(test_db, match1.id, "B1", 12, 1, 1)
        crud.add_player_stats(test_db, match2.id, "B1", 18, 2, 0)
        
        stats = crud.get_player_stats(test_db, "B1")
        assert len(stats) == 2


class TestAnalytics:
    """Testy pro analytické funkce."""
    
    def test_get_leaderboard(self, test_db):
        """Test vytvoření leaderboardu."""
        # Vytvoříme hráče
        crud.create_player(test_db, "A1", "A", "Alice")
        crud.create_player(test_db, "B1", "B", "Bob")
        
        # Vytvoříme zápasy a statistiky
        match = crud.create_match(test_db, 2, 1, 90)
        crud.add_player_stats(test_db, match.id, "A1", 15, 2, 1)
        crud.add_player_stats(test_db, match.id, "B1", 12, 1, 2)
        
        # Leaderboard
        leaderboard = crud.get_leaderboard(test_db, limit=10)
        
        assert len(leaderboard) == 2
        # Alice má více gólů, měla by být první
        assert leaderboard[0]["player_id"] == "A1"
        assert leaderboard[0]["total_goals_scored"] == 2
    
    def test_get_team_stats(self, test_db):
        """Test statistik týmů."""
        # Vytvořit zápasy
        crud.create_match(test_db, 3, 2, 90)
        crud.create_match(test_db, 1, 1, 60)
        
        team_stats = crud.get_team_stats(test_db)
        
        assert team_stats["team_A"]["matches"] == 2
        assert team_stats["team_A"]["total_goals_scored"] == 4  # 3 + 1
        assert team_stats["team_A"]["total_goals_received"] == 3  # 2 + 1
        assert team_stats["team_B"]["total_goals_scored"] == 3  # 2 + 1
        assert team_stats["team_B"]["total_goals_received"] == 4  # 3 + 1

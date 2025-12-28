"""
test_api_endpoints.py – Testy REST API endpointů.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.db import Base, get_db
from api import crud, models


# In-memory SQLite pro testy
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def override_get_db():
    """Override get_db pro FastAPI."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
# Při testech potřebujeme mít registrované modely
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    """Automaticky resetuje databázi před každým testem."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield



@pytest.fixture
def db():
    """Database session pro každý test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


class TestRootEndpoints:
    """Testy root endpointů."""
    
    def test_root(self):
        """Test / endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "MULTIPONG Stats API"
    
    def test_health_check(self):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestPlayersEndpoints:
    """Testy player endpointů."""
    
    def test_list_players_empty(self):
        """Test GET /players/ (prázdná databáze)."""
        response = client.get("/players/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_player(self):
        """Test POST /players/."""
        player_data = {
            "player_id": "A1",
            "name": "Alice",
            "team": "A"
        }
        response = client.post("/players/", json=player_data)
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == "A1"
        assert data["name"] == "Alice"
    
    def test_create_duplicate_player(self):
        """Test vytvoření duplicitního hráče."""
        player_data = {"player_id": "B1", "name": "Bob", "team": "B"}
        
        # První
        response1 = client.post("/players/", json=player_data)
        assert response1.status_code == 200
        
        # Duplicate - mělo by vrátit error
        response2 = client.post("/players/", json=player_data)
        assert response2.status_code == 400
    
    def test_get_player(self):
        """Test GET /players/{player_id}."""
        # Nejdřív vytvoříme
        player_data = {"player_id": "A1", "name": "Alice", "team": "A"}
        client.post("/players/", json=player_data)
        
        # Pak získáme
        response = client.get("/players/A1")
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == "A1"
    
    def test_get_nonexistent_player(self):
        """Test GET neexistujícího hráče."""
        response = client.get("/players/X9")
        assert response.status_code == 404


class TestMatchesEndpoints:
    """Testy match endpointů."""
    
    def test_list_matches_empty(self):
        """Test GET /matches/ (prázdná databáze)."""
        response = client.get("/matches/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_nonexistent_match(self):
        """Test GET neexistujícího zápasu."""
        response = client.get("/matches/999")
        assert response.status_code == 404


class TestStatsEndpoints:
    """Testy stats endpointů."""
    
    def test_leaderboard_empty(self):
        """Test GET /stats/leaderboard (prázdná)."""
        response = client.get("/stats/leaderboard")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_summary_empty(self):
        """Test GET /stats/summary (prázdná)."""
        response = client.get("/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_matches"] == 0
        assert data["total_players"] == 0
        assert data["total_goals"] == 0
    
    def test_team_stats_invalid_team(self):
        """Test GET /stats/team/{team} s neplatným týmem."""
        response = client.get("/stats/team/X")
        assert response.status_code == 400
    
    def test_player_stats_nonexistent(self):
        """Test GET /stats/player/{player_id} neexistujícího."""
        response = client.get("/stats/player/X9")
        assert response.status_code == 404
    
    def test_best_defender_empty(self):
        """Test GET /stats/best_defender (prázdná)."""
        response = client.get("/stats/best_defender")
        assert response.status_code == 404
    
    def test_hottest_scorer_empty(self):
        """Test GET /stats/hottest_scorer (prázdná)."""
        response = client.get("/stats/hottest_scorer")
        assert response.status_code == 404


class TestIntegration:
    """Integrationní testy celého APIflow."""
    
    def test_full_workflow(self, db):
        """Test plného workflowu: vytvoření hráčů, zápasu, statistik."""
        # 1. Vytvoříme hráče
        player1_data = {"player_id": "A1", "name": "Alice", "team": "A"}
        player2_data = {"player_id": "B1", "name": "Bob", "team": "B"}
        
        resp1 = client.post("/players/", json=player1_data)
        resp2 = client.post("/players/", json=player2_data)
        
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        
        # 2. Zkontrolujeme seznam hráčů
        resp = client.get("/players/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2
        
        # 3. Vytvoříme zápas v databázi přímo
        match = crud.create_match(db, team_left_score=3, team_right_score=2, duration_seconds=120)
        
        # 4. Přidáme statistiky
        crud.add_player_stats(db, match.id, "A1", hits=15, goals_scored=2, goals_received=1)
        crud.add_player_stats(db, match.id, "B1", hits=12, goals_scored=1, goals_received=2)
        
        # 5. Zkontrolujeme summary
        resp = client.get("/stats/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_matches"] == 1
        assert data["total_players"] == 2
        assert data["total_goals"] == 3  # 2 + 1

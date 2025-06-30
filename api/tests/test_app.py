import pytest
import os

# Determine the absolute path to the test database and set ENV VAR EARLY
# api/tests/test_app.py -> api/tests/ -> api/
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # This is api/tests
TEST_DB_PATH = os.path.join(TEST_DIR, 'league_data.db') # api/tests/league_data.db
TEST_DATABASE_URI = f'sqlite:///{TEST_DB_PATH}'

# CRITICAL: Set LEAGUE_DB_PATH *before* importing api.app or anything that imports models_base
os.environ['LEAGUE_DB_PATH'] = TEST_DB_PATH

from api.app import app as flask_app # Import the Flask app instance

@pytest.fixture(scope='module')
def app():
    """Fixture to configure the app for testing."""
    # Configure the app instance for testing
    flask_app.config.update({
        "TESTING": True,
        # SQLALCHEMY_DATABASE_URI is for Flask-SQLAlchemy's db object,
        # not directly used by our models_base.py engine, but good practice.
        "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URI,
    })
    # LEAGUE_DB_PATH is already set at the module level.
    # No need to set os.environ['LEAGUE_DB_PATH'] = TEST_DB_PATH here again.
    yield flask_app

@pytest.fixture()
def client(app):
    """Fixture to provide a test client for the app."""
    return app.test_client()

def test_get_game_details_success(client):
    """Test successful retrieval of game details."""
    game_id = "2025 Mid-Season Invitational_Play-In Day 2_2_1"
    response = client.get(f"/games/{game_id}")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = response.get_json()

    assert data["id"] == game_id
    assert data["match"] == "2025 Mid-Season Invitational_Play-In Day 2_2"
    assert data["tournament"] == "MSI 2025"
    assert data["date"] == "2025-06-29 00:15:00" # Verify exact ISO format if critical

    assert data["blue"]["team"]["name"] == "Bilibili Gaming"
    assert data["blue"]["team"]["logo"] == "<url_placeholder>"
    assert data["blue"]["team"]["players"] == ["Bin (Chen Ze-Bin)", "Beichuan", "Knight (Zhuo Ding)", "Elk", "ON"]
    assert data["blue"]["bans"] == ["Twisted Fate", "Azir", "Varus", "Braum", "Kai'Sa"]
    assert data["blue"]["picks"] == ["Rumble", "Xin Zhao", "Annie", "Miss Fortune", "Alistar"]

    assert data["red"]["team"]["name"] == "G2 Esports"
    assert data["red"]["team"]["logo"] == "<url_placeholder>"
    assert data["red"]["team"]["players"] == ["BrokenBlade", "SkewMond", "Caps", "Hans Sama", "Labrov"]
    assert data["red"]["bans"] == ["Poppy", "Taliyah", "Wukong", "Kalista", "Xayah"]
    assert data["red"]["picks"] == ["Ornn", "Pantheon", "Aurora", "Ezreal", "Leona"]

    assert data["winner"] == "blue"

def test_get_game_details_not_found(client):
    """Test retrieval of a non-existent game."""
    game_id = "non_existent_game_id_12345"
    response = client.get(f"/games/{game_id}")

    assert response.status_code == 404
    assert response.content_type == "application/json"

    data = response.get_json()
    assert data["error"] == "Game not found"

def test_root_path(client):
    """Test the root path to ensure the app is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Flask API is running!" in response.data

def test_echo_path(client):
    """Test the /echo path."""
    response = client.post("/echo", json={"message": "hello"})
    assert response.status_code == 200
    assert response.get_json()["echo"] == "hello"

    response_no_message = client.post("/echo", json={})
    assert response_no_message.status_code == 400
    assert response_no_message.get_json()["error"] == "No message provided"

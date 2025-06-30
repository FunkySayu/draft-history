import argparse
import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from .models_base import get_session
from .scoreboard_game_model import ScoreboardGame

app = Flask(__name__)

# Helper function at module level
def _split_comma_separated(cs_string: str | None) -> list[str]:
    if not cs_string:
        return []
    return [item.strip() for item in cs_string.split(',')]

# Database Configuration
db_url_default = 'sqlite:///./app.db'
db_url_env = os.environ.get('DATABASE_URL')

parser = argparse.ArgumentParser(description='Flask API with SQLAlchemy')
parser.add_argument('--db_url', dest='db_url', default=db_url_env or db_url_default,
                    help=f'Database URL (default: {db_url_default}, or DATABASE_URL env var)')
args, unknown = parser.parse_known_args()

app.config['SQLALCHEMY_DATABASE_URI'] = args.db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    return jsonify({"echo": data['message']})

@app.route('/')
def home():
    return "Flask API is running!"

@app.route('/games/<string:game_id>', methods=['GET'])
def get_game_details(game_id: str):
    """
    Retrieves detailed information for a specific game by its ID.

    Args:
        game_id: The unique identifier for the game.

    Returns:
        A JSON response containing the game details if found (200 OK).
        Returns a 404 error if the game_id does not exist.
        Returns a 500 error for other internal server issues.
    """
    session = get_session()
    try:
        game = session.query(ScoreboardGame).filter(ScoreboardGame.GameId == game_id).first()
    except Exception as e:
        app.logger.error(f"Database error while fetching game {game_id}: {e}")
        return jsonify({"error": "Internal server error during database query"}), 500
    finally:
        session.close()

    if not game:
        return jsonify({"error": "Game not found"}), 404

    # If an error occurs during these assignments or in _split_comma_separated,
    # Flask's default error handling will take over (usually resulting in a 500).
    winner_team_str = "blue" if game.Winner == 1 else "red" if game.Winner == 2 else "unknown"
    blue_team_name = game.Team1 if game.Team1 else "Blue Team"
    red_team_name = game.Team2 if game.Team2 else "Red Team"

    response_data = {
        "id": game.GameId,
        "match": game.MatchId,
        "tournament": game.Tournament,
        "date": game.DateTime_UTC,
        "blue": {
            "team": {
                "name": blue_team_name,
                "logo": "<url_placeholder>",
                "players": _split_comma_separated(game.Team1Players),
            },
            "bans": _split_comma_separated(game.Team1Bans),
            "picks": _split_comma_separated(game.Team1Picks),
        },
        "red": {
            "team": {
                "name": red_team_name,
                "logo": "<url_placeholder>",
                "players": _split_comma_separated(game.Team2Players),
            },
            "bans": _split_comma_separated(game.Team2Bans),
            "picks": _split_comma_separated(game.Team2Picks),
        },
        "winner": winner_team_str
    }
    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

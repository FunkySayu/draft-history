import argparse
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
import os

import argparse
import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Local application imports
# Ensure all model modules that define classes using 'Base' from models_base
# are imported here if not handled by models_base.py itself.
# This is to ensure SQLAlchemy's declarative Base knows about all tables.
# For now, ScoreboardGame is directly used, and picks_and_bans_model was added
# to fix a relationship issue. The goal is to make the explicit import of
# picks_and_bans_model here unnecessary by handling it in models_base.py.
from .models_base import get_session # models_base.py now handles registration of all its models
from .scoreboard_game_model import ScoreboardGame # We directly use ScoreboardGame in this file

app = Flask(__name__)

# Database Configuration
# Priority: Command-line arg > Environment Variable > Default
db_url_default = 'sqlite:///./app.db' # Default if no other config is found
db_url_env = os.environ.get('DATABASE_URL')

parser = argparse.ArgumentParser(description='Flask API with SQLAlchemy')
parser.add_argument('--db_url', dest='db_url', default=db_url_env or db_url_default,
                    help=f'Database URL (default: {db_url_default}, or DATABASE_URL env var)')
# Use parse_known_args to allow Gunicorn (or other runners) to pass its own args
args, unknown = parser.parse_known_args()

app.config['SQLALCHEMY_DATABASE_URI'] = args.db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # For Flask-SQLAlchemy specific features, if any. Not directly used by /games endpoint.


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
def get_game_details(game_id):
    session = get_session()
    try:
        game = session.query(ScoreboardGame).filter(ScoreboardGame.GameId == game_id).first()

        if not game:
            return jsonify({"error": "Game not found"}), 404

        # Helper to parse comma-separated strings into a list
        def parse_cs_string(cs_string):
            if not cs_string:
                return []
            return [item.strip() for item in cs_string.split(',')]

        # Determine winner string
        winner_team_str = "blue" if game.Winner == 1 else "red" if game.Winner == 2 else "unknown"

        # Team names (assuming Team1 is Blue, Team2 is Red)
        # These might need adjustment if the game object has more specific team name fields
        # For now, using game.Team1 and game.Team2 as primary names.
        blue_team_name = game.Team1 if game.Team1 else "Blue Team"
        red_team_name = game.Team2 if game.Team2 else "Red Team"


        response_data = {
            "id": game.GameId,
            "match": game.MatchId,
            "tournament": game.Tournament,
            "date": game.DateTime_UTC, # Assuming this is already in ISO 8601 format
            "blue": {
                "team": {
                    "name": blue_team_name,
                    "logo": "<url_placeholder>", # Placeholder as per plan
                    "players": parse_cs_string(game.Team1Players),
                },
                "bans": parse_cs_string(game.Team1Bans),
                "picks": parse_cs_string(game.Team1Picks),
            },
            "red": {
                "team": {
                    "name": red_team_name,
                    "logo": "<url_placeholder>", # Placeholder as per plan
                    "players": parse_cs_string(game.Team2Players),
                },
                "bans": parse_cs_string(game.Team2Bans),
                "picks": parse_cs_string(game.Team2Picks),
            },
            "winner": winner_team_str
        }
        return jsonify(response_data), 200
    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Error fetching game {game_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()

if __name__ == '__main__':
    # The db.create_all() call is typically used for models defined with Flask-SQLAlchemy's db.Model.
    # Since ScoreboardGame and PicksAndBansS7Model are defined using a separate Base
    # and initialized via db_setup.py, db.create_all() is not needed here for those tables.
    # If this app were to have its own Flask-SQLAlchemy models, then it would be relevant.
    app.run(host='0.0.0.0', port=5000)

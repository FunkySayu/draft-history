import argparse
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
import os

# Database Configuration
# Priority: Command-line arg > Environment Variable > Default
# Example: python app.py --db_url sqlite:///./test.db
# Docker: Set DATABASE_URL environment variable in docker-compose.yml
db_url_default = 'sqlite:///./app.db'
db_url_env = os.environ.get('DATABASE_URL')

parser = argparse.ArgumentParser(description='Flask API with SQLAlchemy')
parser.add_argument('--db_url', dest='db_url', default=db_url_env or db_url_default,
                    help=f'Database URL (default: {db_url_default}, or DATABASE_URL env var)')
args, unknown = parser.parse_known_args() # Use parse_known_args to ignore Gunicorn args

app.config['SQLALCHEMY_DATABASE_URI'] = args.db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Example Model (can be removed or modified)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Message {self.id}>'

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    return jsonify({"echo": data['message']})

@app.route('/')
def home():
    return "Flask API is running!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Create tables if they don't exist
    app.run(host='0.0.0.0', port=5000)

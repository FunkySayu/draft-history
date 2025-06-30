import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ensure the data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data') # Relative to this file's location in api/
os.makedirs(DATA_DIR, exist_ok=True)

# Allow overriding the database path via environment variable
_DEFAULT_DB_FILE = os.path.join(DATA_DIR, 'league_data.db')
_DB_FILE_PATH = os.environ.get('LEAGUE_DB_PATH', _DEFAULT_DB_FILE)

# Ensure the directory for the database exists
os.makedirs(os.path.dirname(_DB_FILE_PATH), exist_ok=True)

DATABASE_URL = f"sqlite:///{_DB_FILE_PATH}"
# print(f"Using database at: {DATABASE_URL}") # For verification - removed as requested

engine = create_engine(DATABASE_URL, echo=False) # Disabled echo for cleaner collect_data output
Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()

def init_db():
    # Import all modules here that define models so that
    # they are registered with the Base metadata. Otherwise,
    # Base.metadata.create_all(engine) may not find them.
    # This is a common pattern for SQLAlchemy model organization.
    from . import scoreboard_game_model # noqa F401
    from . import picks_and_bans_model # noqa F401
    Base.metadata.create_all(bind=engine)
    # print(f"Database initialized/updated at {DATABASE_URL}") # Keep this silent unless debugging

if __name__ == "__main__":
    # This allows creating the DB schema by running: python -m api.models_base
    # However, db_setup.py will be the primary script for this.
    init_db() # Actually run it if script is called directly
    print("Database tables created/verified via models_base.py direct execution.")

# Ensure all models are imported when models_base is imported.
# This helps SQLAlchemy's Base collect all model metadata.
# The # noqa F401 silences flake8 unused import warnings, as they are needed for registration.
from . import scoreboard_game_model # noqa: F401
from . import picks_and_bans_model  # noqa: F401

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ensure the data directory for the default DB exists (though test DB path is now preferred for tests)
_DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(_DEFAULT_DATA_DIR, exist_ok=True)

_DEFAULT_DB_FILE = os.path.join(_DEFAULT_DATA_DIR, 'league_data.db')
_DB_FILE_PATH = os.environ.get('LEAGUE_DB_PATH', _DEFAULT_DB_FILE)

# Ensure the directory for the database exists, especially if LEAGUE_DB_PATH is used
os.makedirs(os.path.dirname(_DB_FILE_PATH), exist_ok=True)

DATABASE_URL = f"sqlite:///{_DB_FILE_PATH}"
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Provides a new SQLAlchemy session."""
    return SessionLocal()

def init_db():
    """
    Initializes the database by creating all tables defined by models
    that inherit from the Base metadata.
    This function is typically called by database setup scripts.
    """
    Base.metadata.create_all(bind=engine)

# Ensure all models are imported when models_base is imported.
# This helps SQLAlchemy's Base collect all model metadata.
# The # noqa F401 silences flake8 unused import warnings, as they are needed for registration.
from . import scoreboard_game_model # noqa: F401
from . import picks_and_bans_model  # noqa: F401

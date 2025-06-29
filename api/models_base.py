import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ensure the data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data') # Relative to this file's location in api/
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'league_data.db')}"

engine = create_engine(DATABASE_URL, echo=True) # Enabled echo for debugging
Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()

def init_db():
    # Import all modules here that define models so that
    # they are registered with the Base metadata. Otherwise,
    # Base.metadata.create_all(engine) may not find them.
    # This is a common pattern for SQLAlchemy model organization.
    from . import scoreboard_game_model # noqa
    from . import picks_and_bans_model # noqa
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized/updated at {DATABASE_URL}")

if __name__ == "__main__":
    # This allows creating the DB schema by running: python -m api.models_base
    # However, db_setup.py will be the primary script for this.
    # For now, just prints that it would initialize.
    print("This script defines DB base and engine. Run db_setup.py to create tables.")

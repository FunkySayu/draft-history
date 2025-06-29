from ..models_base import init_db

def create_tables():
    """
    Creates database tables based on SQLAlchemy models.
    The actual table creation logic is in models_base.init_db(),
    which also prints confirmation.
    """
    init_db()

if __name__ == '__main__':
    create_tables()

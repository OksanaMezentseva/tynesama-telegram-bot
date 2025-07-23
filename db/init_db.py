from db.session import engine
from db.db_models import base, user, feedback

def init_db():
    """
    Initialize all database tables defined in the models.
    """
    base.Base.metadata.create_all(bind=engine)
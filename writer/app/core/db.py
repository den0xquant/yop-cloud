from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    This function should be called at the start of the application.
    """
    SQLModel.metadata.create_all(engine)


def get_db_session():
    """
    Create a new SQLAlchemy session.

    Returns:
        Session: A new SQLAlchemy session.
    """
    with Session(engine) as session:
        yield session

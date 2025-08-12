from unittest.mock import AsyncMock, MagicMock
import pytest

from fastapi.testclient import TestClient

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.db import get_db_session
from app.main import app
from app.services.db import FileRepository
from app.services.s3 import FileStreamer, S3ClientManager


SQLITE_DATABASE_URL = "sqlite://"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_db_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="repo")
def repo_fixture(session: Session):
    return FileRepository(session)


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.put_object = AsyncMock()
    client.get_object = AsyncMock()
    return client


@pytest.fixture
def file_streamer(mock_session):
    return FileStreamer()
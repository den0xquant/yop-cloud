import uuid

from app.services.db import FileRepository
from app.schemas.models import FileCreate
from app.schemas.orm import File, ChunkPerFile


def create_file(repo: FileRepository) -> File:
    fc = FileCreate(name="file.txt")
    return repo.save_file(fc)


def test_create_and_retrieve_file(repo: FileRepository):
    created_file = create_file(repo)
    retrieved_file = repo.get_file_by_id(file_id=created_file.id)

    assert created_file.id is not None
    assert retrieved_file is not None
    assert created_file.name == retrieved_file.name
    assert isinstance(created_file, File)
    assert created_file == retrieved_file
    assert created_file.is_ready is False


def test_get_nonexistent_file_returns_none(repo: FileRepository):
    assert repo.get_file_by_id(file_id=uuid.uuid4()) is None


def test_file_failed(repo: FileRepository):
    missing_id = uuid.uuid4()
    repo.set_file_failed(missing_id)

    missing_file = repo.get_file_by_id(file_id=missing_id)
    assert missing_file is None


def test_file_completed(repo: FileRepository):
    missing_id = uuid.uuid4()
    repo.set_file_completed(missing_id)

    missing_file = repo.get_file_by_id(file_id=missing_id)
    assert missing_file is None


def test_save_chunk_and_get_chunks(repo: FileRepository):
    file = create_file(repo)

    repo.save_chunk(file_id=file.id, chunk_hash="h3", index=3)
    repo.save_chunk(file_id=file.id, chunk_hash="h2", index=2)
    repo.save_chunk(file_id=file.id, chunk_hash="h1", index=1)

    chunks = repo.get_file_chunks(file_id=file.id)
    assert [c.index for c in chunks] == [1, 2, 3]
    assert [c.chunk_hash for c in chunks] == ["h1", "h2", "h3"]
    assert all(isinstance(c, ChunkPerFile) for c in chunks)


def test_set_file_failed_and_completed_toggle(repo: FileRepository):
    f = create_file(repo)
    repo.set_file_completed(file_id=f.id)
    fresh_file = repo.get_file_by_id(file_id=f.id)

    assert fresh_file is not None
    assert fresh_file.is_ready is True

    repo.set_file_failed(file_id=f.id)
    fresh_file_2 = repo.get_file_by_id(file_id=f.id)

    assert fresh_file_2 is not None
    assert fresh_file.is_ready is False

import uuid
from typing import Protocol, Sequence

from app.schemas.models import FileCreate
from app.schemas.orm import File, ChunkPerFile


class Database(Protocol):
    def save_file(self, file_create: FileCreate) -> File:  # type: ignore
        pass

    def save_chunk(self, file_id: uuid.UUID, chunk_hash: str, index: int) -> None:
        pass

    def get_file_by_id(self, file_id: uuid.UUID) -> File | None:
        pass

    def get_filename_by_id(self, file_id: uuid.UUID) -> str:  # type: ignore
        pass

    def get_file_chunks(self, file_id: uuid.UUID) -> Sequence[ChunkPerFile]:  # type: ignore
        pass

    def set_file_failed(self, file_id: uuid.UUID) -> None:
        pass

    def set_file_completed(self, file_id: uuid.UUID) -> None:
        pass


class S3(Protocol):
    async def upload_chunk(self, chunk: bytes, key: str) -> None:
        pass

import uuid
from typing import AsyncGenerator, Protocol, Sequence

from app.schemas.models import FileCreate
from app.schemas.orm import File, ChunkPerFile


class Database(Protocol):
    def get_file_by_id(self, file_id: uuid.UUID) -> File | None:
        pass

    def get_file_chunks(self, file_id: uuid.UUID) -> Sequence[ChunkPerFile]:  # type: ignore
        pass


class S3(Protocol):
    def get_chunk_stream(self, *, key: str) -> AsyncGenerator[bytes, None]:  # type: ignore
        pass

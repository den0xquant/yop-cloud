import uuid
from typing import Protocol, Sequence
from aiobotocore.response import StreamingBody

from app.schemas.models import FileCreate
from app.schemas.orm import File, ChunkPerFile


class Database(Protocol):
    def save_file(self, file_create: FileCreate) -> File: pass # type: ignore
    def save_chunk(self, file_id: uuid.UUID, chunk_hash: str) -> None: pass
    def get_file_by_id(self, file_id: uuid.UUID) -> File | None: pass
    def get_filename_by_id(self, file_id: uuid.UUID) -> str: pass # type: ignore
    def get_file_chunks(self, file_id: uuid.UUID) -> Sequence[ChunkPerFile]: pass # type: ignore


class S3(Protocol):
    async def get_chunk_stream(self, key: str) -> StreamingBody: pass # type: ignore
    async def upload_chunk(self, chunk: bytes, key: str) -> None: pass

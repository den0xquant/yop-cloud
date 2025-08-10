"""Content Addressable Storage"""

import logging
from typing import AsyncGenerator
import uuid

from app.services.ports import Database, S3
from app.schemas.models import FileBase


log = logging.getLogger(__name__)


class FileStorageService:
    """
    Service for managing file storage using a content-addressable storage (CAS) approach.

    Responsibilities:
        - Split uploaded files into fixed-size chunks.
        - Calculate a stable hash for each chunk.
        - Store chunk metadata in the database (mapping file_id -> chunk_hash -> index).
        - Upload chunks to an S3-compatible object storage.
        - Stream files back to the client by reading chunks sequentially from storage.

    Dependencies:
        db (Database): Abstract interface for file/chunk metadata persistence.
        s3 (S3): Abstract interface for S3-compatible storage operations.
    """
    def __init__(self, db: Database, s3: S3):
        self.db = db
        self.s3 = s3

    def get_file_object(self, file_id: uuid.UUID) -> FileBase:
        file_obj = self.db.get_file_by_id(file_id)
        return FileBase.model_validate(file_obj)

    async def stream_file(self, file_id: uuid.UUID) -> AsyncGenerator[bytes, None]:
        chunks = self.db.get_file_chunks(file_id)

        if not chunks:
            raise FileNotFoundError(f"No chunks for file {file_id}")

        for chunk_meta in chunks:
            chunk_key = chunk_meta.chunk_hash

            try:
                async for chunk in self.s3.get_chunk_stream(key=chunk_key):
                    yield chunk

            except Exception as e:
                log.exception(f"Failed to stream chunk: {chunk_key}")
                log.exception(f"Error {e}")
                raise ValueError("Something went wrong")

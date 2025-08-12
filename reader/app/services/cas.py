"""Content Addressable Storage"""

import logging
import hashlib
from typing import AsyncGenerator
import uuid
import secrets
from fastapi import UploadFile

from app.core.config import settings
from app.schemas.models import FileCreate, FileBase
from app.services.ports import Database, S3


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

    @staticmethod
    def get_chunk_hash(chunk: bytes) -> str:
        return hashlib.sha256(chunk).hexdigest()

    @staticmethod
    def get_random_string(n: int) -> str:
        return secrets.token_urlsafe(n)

    def get_filename(self, file_id: uuid.UUID) -> str:
        return self.db.get_filename_by_id(file_id)

    def get_file_object(self, file_id: uuid.UUID) -> FileBase:
        file_obj = self.db.get_file_by_id(file_id)
        return FileBase.model_validate(file_obj)

    async def upload_file(self, file: UploadFile) -> str:
        filename = file.filename or self.get_random_string(20)
        content_type = file.content_type or "application/octet-stream"

        index = 0

        try:
            file_obj = self.db.save_file(file_create=FileCreate(name=filename))
            file_id = file_obj.id

            while chunk := await file.read(settings.CHUNK_SIZE):
                s3_key = self.get_chunk_hash(chunk)
                await self.s3.upload_chunk(chunk=chunk, key=s3_key)
                self.db.save_chunk(file_id=file_id, chunk_hash=s3_key, index=index)
                index += 1

            if index == 0:
                self.db.set_file_failed(file_id)
                raise ValueError("Empty file upload is not allowed")

            self.db.set_file_completed(file_id)
            log.info(f"File uploaded: {file_id}, content_type={content_type}")
            return str(file_id)

        except Exception:
            try:
                self.db.set_file_failed(file_id)
            finally:
                pass
            raise

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

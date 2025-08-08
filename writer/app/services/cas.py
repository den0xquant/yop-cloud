"""Content Addressable Storage"""
import uuid
import secrets
from fastapi import UploadFile

from app.core.config import settings
from app.schemas.models import FileCreate
from app.services.ports import Database, S3


class FileStorageService:
    def __init__(self, db: Database, s3: S3):
        self.db = db
        self.s3 = s3

    def get_s3_key_hash(self, chunk: bytes) -> str:
        return str(hash(chunk))

    def get_random_string(self, n: int) -> str:
        return secrets.token_urlsafe(n)
    
    def get_filename(self, file_id: uuid.UUID) -> str:
        return self.db.get_filename_by_id(file_id)

    async def upload_file(self, file: UploadFile) -> str:
        filename = file.filename if file.filename is not None else self.get_random_string(20)
        try:
            file_create = FileCreate(name=filename)
            file_obj = self.db.save_file(file_create=file_create)

            while chunk := await file.read(settings.CHUNK_SIZE):
                s3_key = self.get_s3_key_hash(chunk)
                await self.s3.upload_chunk(chunk=chunk, key=s3_key)
                self.db.save_chunk(file_id=file_obj.id, chunk_hash=s3_key)

        except Exception:
            raise

        return "OK"

    async def stream_file(self, file_id: uuid.UUID):
        chunks = self.db.get_file_chunks(file_id)

        for rec in chunks:
            body_stream = await self.s3.get_chunk_stream(key=rec.chunk_hash)
            while True:
                part = await body_stream.read(settings.CHUNK_SIZE)
                if not part:
                    break
                yield part

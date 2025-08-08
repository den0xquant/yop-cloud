from typing import Sequence
import uuid
from sqlmodel import Session, select

from app.schemas.models import FileCreate, ChunkPerFileBase
from app.schemas.orm import File, ChunkPerFile


class FileRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_file(self, file_create: FileCreate) -> File:
        file_obj = File.model_validate(file_create)
        self.session.add(file_obj)
        self.session.commit()
        self.session.refresh(file_obj)
        return file_obj

    def save_chunk(self, file_id: uuid.UUID, chunk_hash: str) -> None:
        idx = 0  # TODO: Calc index correctly

        chunk_create = ChunkPerFileBase(
            file_id=file_id, chunk_hash=chunk_hash, index=idx
        )
        chunk_obj = ChunkPerFile.model_validate(chunk_create)

        self.session.add(chunk_obj)
        self.session.commit()

    def get_file_by_id(self, file_id: uuid.UUID) -> File | None:
        statement = select(File).where(File.id == file_id)
        file_obj = self.session.exec(statement).first()
        return file_obj

    def get_filename_by_id(self, file_id: uuid.UUID) -> str:
        statement = select(File.name).where(File.id == file_id)
        filename = self.session.exec(statement).one()
        return filename

    def get_file_chunks(self, file_id: uuid.UUID) -> Sequence[ChunkPerFile]:
        statement = select(ChunkPerFile).where(ChunkPerFile.file_id == file_id)
        chunks = self.session.exec(statement).all()
        return chunks

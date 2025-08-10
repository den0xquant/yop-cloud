import logging
from typing import Sequence
import uuid
from sqlmodel import Session, select, col

from app.schemas.models import FileCreate, ChunkPerFileBase
from app.schemas.orm import File, ChunkPerFile


log = logging.getLogger(__name__)


class FileRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_file_by_id(self, file_id: uuid.UUID) -> File | None:
        statement = select(File).where(File.id == file_id)
        file_obj = self.session.exec(statement).first()
        return file_obj

    def get_file_chunks(self, file_id: uuid.UUID) -> Sequence[ChunkPerFile]:
        statement = (
            select(ChunkPerFile)
            .where(ChunkPerFile.file_id == file_id)
            .order_by(col(ChunkPerFile.index).asc())
        )
        chunks = self.session.exec(statement).all()
        return chunks

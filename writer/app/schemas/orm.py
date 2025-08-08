import uuid
from sqlmodel import Field, Relationship

from app.schemas.models import FileBase, ChunkPerFileBase


class File(FileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chunks: list["ChunkPerFile"] = Relationship(back_populates="file", cascade_delete=False)


class ChunkPerFile(ChunkPerFileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    file_id: uuid.UUID = Field(
        foreign_key="file.id", nullable=True, ondelete="SET NULL"
    )
    file: File = Relationship(back_populates="chunks")

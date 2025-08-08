from enum import StrEnum
import uuid

from sqlmodel import SQLModel


class FileType(StrEnum):
    FILE = "file"
    DIRECTORY = "directory"


class FileCreate(SQLModel):
    name: str


class FileBase(FileCreate):
    parent_id: int = -1
    file_type: FileType = FileType.FILE
    is_ready: bool = False


class ChunkPerFileBase(SQLModel):
    file_id: uuid.UUID
    chunk_hash: str
    index: int

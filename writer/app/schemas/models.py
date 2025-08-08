from typing import Literal

from sqlmodel import SQLModel


class FileBase(SQLModel):
    name: str
    parent_id: int = -1
    file_type: Literal["FILE", "DIRECTORY"] = "FILE"
    is_ready: bool = False


class ChunkPerFileBase(SQLModel):
    file_id: int
    chunk_hash: str
    index: int

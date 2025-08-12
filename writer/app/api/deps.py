from typing import Annotated
from fastapi import Depends, Request
from sqlmodel import Session

from app.services.ports import Database, S3
from app.services.cas import FileStorageService
from app.services.db import FileRepository
from app.services.s3 import FileStreamer
from app.core.db import get_db_session


SessionDependency = Annotated[Session, Depends(get_db_session)]


def get_repository(session: SessionDependency) -> Database:
    return FileRepository(session=session)


def get_streamer(request: Request) -> S3:
    client_manager = request.app.state.s3_manager
    return FileStreamer(manager=client_manager)


RepositoryDependency = Annotated[Database, Depends(get_repository)]
StreamerDependency = Annotated[S3, Depends(get_streamer)]


def get_storage(db: RepositoryDependency, s3: StreamerDependency) -> FileStorageService:
    return FileStorageService(db=db, s3=s3)


CASDependency = Annotated[FileStorageService, Depends(get_storage)]

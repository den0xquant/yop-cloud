from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from types_aiobotocore_s3.client import S3Client

from app.services.ports import Database, S3
from app.services.cas import FileStorageService
from app.services.db import FileRepository
from app.services.s3 import FileStreamer
from app.core.db import get_db_session
from app.core.s3 import get_s3_client


SessionDependency = Annotated[Session, Depends(get_db_session)]
S3ClientDependency = Annotated[S3Client, Depends(get_s3_client)]


def get_repository(session: SessionDependency) -> Database:
    return FileRepository(session=session)


def get_streamer(s3client: S3ClientDependency) -> S3:
    return FileStreamer(s3client=s3client)


RepositoryDependency = Annotated[Database, Depends(get_repository)]
StreamerDependency = Annotated[S3, Depends(get_streamer)]


def get_storage(db: RepositoryDependency, s3: StreamerDependency) -> FileStorageService:
    return FileStorageService(db=db, s3=s3)


CASDependency = Annotated[FileStorageService, Depends(get_storage)]

from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from types_aiobotocore_s3.client import S3Client

from app.core.db import get_db_session
from app.core.s3 import get_s3_client


SessionDependency = Annotated[Session, Depends(get_db_session)]
S3ClientDependency = Annotated[S3Client, Depends(get_s3_client)]

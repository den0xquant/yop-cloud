from fastapi import APIRouter, UploadFile

from app.core.config import settings
from app.api.deps import SessionDependency, S3ClientDependency
from app.services.upload import process_chunk


api_router = APIRouter(prefix="/upload", tags=["writer"])


@api_router.post("/")
async def upload(*, file: UploadFile, session: SessionDependency, s3client: S3ClientDependency):
    i = 0
    while chunk := await file.read(settings.CHUNK_SIZE):
        await s3client.put_object(Bucket="yop-cloud-bucket", Key=f"filename{i}", Body=chunk)
        i += 1

    return {"message": "OK"}

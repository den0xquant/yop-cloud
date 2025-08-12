from fastapi import (
    APIRouter,
    UploadFile,
)

from app.api.deps import CASDependency


api_router = APIRouter(tags=["writer"])


@api_router.post("/upload", name="upload_file")
async def upload(*, file: UploadFile, fs: CASDependency) -> str:
    return await fs.upload_file(file)

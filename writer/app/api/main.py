import uuid
from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from app.api.deps import CASDependency


api_router = APIRouter(prefix="/upload", tags=["writer"])


@api_router.post("/")
async def upload(*, file: UploadFile, fs: CASDependency) -> str:
    return await fs.upload_file(file)


# TODO: MOVE TO READER SERVICE
@api_router.get("/download")
async def download(*, file_id: uuid.UUID, fs: CASDependency):
    filename = fs.get_filename(file_id)
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Accept-Ranges": "none",
    }
    return StreamingResponse(
        fs.stream_file(file_id=file_id),
        media_type="application/octet-stream",
        headers=headers,
        status_code=200,
    )

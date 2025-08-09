import uuid
from fastapi import APIRouter, UploadFile, Request
from fastapi.responses import StreamingResponse

from app.api.deps import CASDependency


api_router = APIRouter(prefix="/upload", tags=["writer"])


@api_router.post("/", name="upload_file")
async def upload(*, file: UploadFile, fs: CASDependency) -> str:
    return await fs.upload_file(file)


# TODO: MOVE TO READER SERVICE
@api_router.get("/download/{file_id}", name="download_file")
async def download(*, request: Request, file_id: uuid.UUID, fs: CASDependency):
    media_type = "application/octet-stream"
    filename = fs.get_filename(file_id)

    accept = (request.headers.get("accept") or "").lower()
    if "application/octet-stream" not in accept and "*/*" not in accept:
        download_url = str(request.url_for("download_file", file_id=str(file_id)))
        return {
            "file_id": str(file_id),
            "filename": filename,
            "download_url": download_url,
        }

    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Accept-Ranges": "none",
    }
    return StreamingResponse(
        fs.stream_file(file_id=file_id),
        media_type=media_type,
        headers=headers,
        status_code=200,
    )

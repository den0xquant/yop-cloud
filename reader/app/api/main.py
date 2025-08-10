import uuid
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import CASDependency


api_router = APIRouter(prefix="/download", tags=["reader"])


@api_router.get("/{file_id}", name="download_file")
async def download(*, request: Request, file_id: uuid.UUID, fs: CASDependency):
    media_type = "application/octet-stream"
    file = fs.get_file_object(file_id)
    filename = file.name

    if not file.is_ready:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not ready for downloading"
        )

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
        status_code=status.HTTP_200_OK,
    )

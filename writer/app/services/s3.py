from aiobotocore.response import StreamingBody
from types_aiobotocore_s3.client import S3Client

from app.core.config import settings


class FileStreamer:
    def __init__(self, s3client: S3Client) -> None:
        self.s3client = s3client

    async def get_chunk_stream(self, key: str) -> StreamingBody:
        resp = await self.s3client.get_object(Bucket=settings.AWS_BUCKET_NAME, Key=key)
        return resp["Body"]

    async def upload_chunk(self, chunk: bytes, key: str) -> None:
        await self.s3client.put_object(
            Bucket=settings.AWS_BUCKET_NAME, Key=key, Body=chunk
        )

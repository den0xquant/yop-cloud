import asyncio
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Generator
from aiobotocore.response import StreamingBody
from types_aiobotocore_s3.client import S3Client

from app.core.config import settings


log = getLogger(__name__)


class FileStreamer:
    def __init__(self, s3client: S3Client) -> None:
        self.s3client = s3client
        self.bucket = settings.AWS_BUCKET_NAME

    async def get_chunk_stream(self, key: str):
        resp = await self.s3client.get_object(Bucket=self.bucket, Key=key)
        log.info(f"type: {type(resp["Body"])} body: {resp["Body"]}")
        return resp["Body"]

    async def upload_chunk(self, chunk: bytes, key: str, attempts: int = 3) -> None:
        delay = 0.1

        for i in range(attempts):
            try:
                await self.s3client.put_object(
                    Bucket=settings.AWS_BUCKET_NAME, Key=key, Body=chunk
                )
            except Exception as e:
                if i == attempts - 1:
                    log.exception(f"S3 put_object failed after retries: key={key}")
                    raise
                log.warning(f"S3 put_object retrying: {i+1}/{attempts}. Error: {e}")
                await asyncio.sleep(delay)
                delay *= 2

import asyncio
from typing import AsyncGenerator
from aiobotocore.session import get_session, AioSession
from aiohttp import ClientError
from botocore.config import Config
from contextlib import AsyncExitStack
from logging import getLogger

from app.services.ports import S3Like
from app.core.config import settings


log = getLogger(__name__)


class S3ClientManager:
    def __init__(
            self,
            session: AioSession | None = None,
            config: Config | None = None,
        ):
        self.session: AioSession = session or get_session()
        self._config = config or Config(
            signature_version=settings.AWS_SIGNATURE_VERSION,
            max_pool_connections=50,
            connect_timeout=10,
            read_timeout=30,
            retries={"max_attempts": 3}
        )
        self._stack: AsyncExitStack | None = None
        self.client: S3Like | None = None

    async def start(self) -> None:
        if self.client is not None:
            return
        self._stack = AsyncExitStack()
        self.client = await self._stack.enter_async_context(
            self.session.create_client(
                service_name=settings.AWS_SERVICE_NAME,
                endpoint_url=settings.AWS_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION_NAME,
                config=self._config
            )
        )

    async def close(self) -> None:
        if self._stack is not None:
            await self._stack.aclose()
        self.client = None
        self._stack = None

    def get_client(self) -> S3Like:
        if self.client is None:
            raise RuntimeError("S3ClientManager is not started. Call await start()")
        return self.client


class FileStreamer:
    def __init__(
            self,
            manager: S3ClientManager | None = None,
            bucket: str | None = None,
        ):
        self._manager = manager or S3ClientManager()
        self.bucket = bucket or settings.AWS_BUCKET_NAME

    async def upload_chunk(self, chunk: bytes, key: str, attempts: int = 3) -> None:
        client = self._manager.get_client()
        delay = 0.1

        for attempt in range(1, attempts + 1):
            try:
                await client.put_object(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Key=key,
                    Body=chunk,
                )
                return
            except ClientError as e:
                if attempt == attempts:
                    log.exception(f"S3 put_object failed after retries: key={key}")
                    raise
                log.warning(f"S3 put_object retrying: {attempt}/{attempts+1}. Error: {e}")
                await asyncio.sleep(delay)
                delay *= 2
    
    async def _maybe_close_io(self, body):
        try:
            close = getattr(body, "close", None)
            if close is None:
                return
            res = close()
            if asyncio.iscoroutine(res):
                await res
        except Exception:
            pass

    async def get_chunk_stream(self, *, key: str, attempts: int = 3) -> AsyncGenerator[bytes, None]:
        client = self._manager.get_client()
        delay = 0.1

        for attempt in range(1, attempts + 1):
            try:
                response = await client.get_object(Bucket=self.bucket, Key=key)
                body = response["Body"]

                try:
                    async for chunk in body.iter_chunks(settings.READ_CHUNK):
                        yield chunk
                    return
                finally:
                    await self._maybe_close_io(body)

            except ClientError as e:
                if attempt == attempts:
                    log.exception(f"S3 get_object failed after retries: key={key}")
                    raise
                log.warning(f"S3 get_object retrying: {attempt}/{attempts+1}. Error: {e}")
                await asyncio.sleep(delay)
                delay *= 2

import asyncio
from typing import AsyncGenerator
from aiobotocore.session import get_session
from botocore.config import Config
from contextlib import AsyncExitStack
from logging import getLogger

from app.core.config import settings


log = getLogger(__name__)


class FileStreamer:
    def __init__(self):
        self.session = get_session()
        self.bucket = settings.AWS_BUCKET_NAME
        self.client = None
    
    async def create_client(self, exit_stack: AsyncExitStack):
        if self.client is not None:
            return self.client
        
        self.client = await exit_stack.enter_async_context(
            self.session.create_client(
                service_name=settings.AWS_SERVICE_NAME,
                endpoint_url=settings.AWS_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION_NAME,
                config=Config(
                    signature_version=settings.AWS_SIGNATURE_VERSION,
                    max_pool_connections=50,
                    connect_timeout=10,
                    read_timeout=30,
                    retries={"max_attempts": 3}
                )
            )
        )
        return self.client

    async def get_chunk_stream(self, *, key: str) -> AsyncGenerator[bytes, None]:
        async with AsyncExitStack() as exit_stack:
            s3_client = await self.create_client(exit_stack)
            response = await s3_client.get_object(Bucket=self.bucket, Key=key)

            try:
                async for chunk in response["Body"].iter_chunks(settings.READ_CHUNK):
                    yield chunk
            finally:
                try:
                    response["Body"].close()
                except Exception as e:
                    log.error(f"Failed to close StreamingBody {e}")
                    pass

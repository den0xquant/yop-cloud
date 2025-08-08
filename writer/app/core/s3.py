from botocore.client import Config
from aiobotocore.session import get_session

from app.core.config import settings


async def get_s3_client():
    session = get_session()
    async with session.create_client(
        service_name=settings.AWS_SERVICE_NAME,
        endpoint_url=settings.AWS_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME,
        config=Config(signature_version=settings.AWS_SIGNATURE_VERSION),
    ) as client:
        yield client

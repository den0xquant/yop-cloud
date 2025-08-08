from botocore.client import Config
from aiobotocore.session import get_session


async def get_s3_client():
    session = get_session()
    async with session.create_client(
        service_name="s3",
        endpoint_url=,
        aws_access_key_id=",
        aws_secret_access_key=,
        region_name="us-east-1",
        config=Config(signature_version='s3v4')
    ) as client:
        yield client

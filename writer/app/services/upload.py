from fastapi import UploadFile


async def process_chunk(s3client, data: bytes) -> str:
    # 1. Save chunk to s3
    ...
    return "OK"

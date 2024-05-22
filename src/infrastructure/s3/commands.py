import os
import io
import mimetypes
from uuid import UUID
from dotenv import load_dotenv

from src.infrastructure.s3.factory import get_s3_session

from fastapi.responses import StreamingResponse

load_dotenv()


async def s3_media_upload(
        file, key: UUID, ext: str
) -> None:
    session = get_s3_session()
    async with session.client('s3') as s3:
        await s3.put_object(
            ACL="bucket-owner-full-control",
            Body=file,
            Bucket=os.environ["AWS_S3_BUCKET"],
            ContentEncoding="UTF-8",
            Key=str(key) + ext,
        )


async def s3_get_media(key: UUID, ext: str) -> StreamingResponse:
    session = get_s3_session()
    file_name = str(key) + ext
    async with session.client("s3") as s3:
        response = await s3.get_object(
            Bucket=os.environ["AWS_S3_BUCKET"],
            Key=file_name
        )
        async with response["Body"] as stream:
            content = await stream.read()
            content_type = mimetypes.guess_type(file_name)
            return StreamingResponse(
                io.BytesIO(content),
                media_type=content_type[0]
            )

from uuid import UUID


async def s3_media_upload(
        bucket: str, file, key: UUID, ext: str, s3_client
) -> None:
    async with s3_client as s3:
        await s3.put_object(
            ACL="bucket-owner-full-control",
            Body=file,
            Bucket=bucket,
            ContentEncoding="UTF-8",
            Key=str(key) + ext,
        )


async def s3_get_entry(bucket: str, key: UUID, s3_client) -> str:
    async with s3_client as s3:
        res = await s3.get_object(Bucket=bucket, Key=str(key) + ".txt")
        content = await res["Body"].read()
        return content.decode()

import os
from typing import Any

import aioboto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from boto3.session import Session

load_dotenv()


class S3Singleton:
    __instance = None

    def __init__(self) -> None:
        self.client = aioboto3.Session(
            region_name=os.environ["AWS_REGION_NAME"],
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        ).client("s3")

    def __new__(cls, *args: Any, **kwargs: Any) -> "S3Singleton":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    @property
    def bucket_name(self) -> str:
        name = os.getenv("AWS_S3_BUCKET")
        if not name:
            raise ValueError("Could not get bucket name")
        return name


def get_s3() -> S3Singleton:
    return S3Singleton()


def exist_bucket():
    s3_client = Session(
        region_name=os.environ["AWS_REGION_NAME"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    ).client('s3')
    try:
        s3_client.head_bucket(Bucket=os.environ["AWS_S3_BUCKET"])
    except ClientError:
        s3_client.create_bucket(
            Bucket=os.environ["AWS_S3_BUCKET"],
            CreateBucketConfiguration={
                'LocationConstraint': os.environ["AWS_REGION_NAME"]
            }
        )

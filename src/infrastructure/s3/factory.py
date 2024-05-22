import os
import aioboto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from boto3.session import Session

load_dotenv()


def get_s3_session():
    return aioboto3.Session(
        region_name=os.environ["AWS_REGION_NAME"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )


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

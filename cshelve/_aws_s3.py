from typing import Any, Dict, Iterator

import boto3
from botocore.exceptions import ClientError

from .exceptions import key_access
from .provider_interface import ProviderInterface


class AwsS3(ProviderInterface):
    def __init__(self, logger) -> None:
        self.logger = logger
        self.bucket_name = None
        self.s3 = None
        self.aws_access_key_id = None
        self.aws_secret_access_key = None

    def close(self) -> None:
        # No specific close operation needed for boto3 client
        pass

    def configure_default(self, config: Dict[str, str]) -> None:
        # Example configuration, can be extended as needed
        self.bucket_name = config.get("bucket_name")
        self.aws_access_key_id = config.get("key_id")
        self.aws_secret_access_key = config.get("key_secret")

    def configure_logging(self, config: Dict[str, str]) -> None:
        # Configure logging if needed
        pass

    def set_provider_params(self, provider_params: Dict[str, Any]) -> None:
        # Set any additional parameters if needed
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            **provider_params,
        )

    def contains(self, key: bytes) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=key.decode("utf-8"))
            return True
        except ClientError:
            return False

    def create(self) -> None:
        self.s3.create_bucket(Bucket=self.bucket_name)

    def delete(self, key: bytes) -> None:
        # Silently ignore if the key does not exist.
        self.s3.delete_object(Bucket=self.bucket_name, Key=key.decode("utf-8"))

    def exists(self) -> bool:
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False

    @key_access(ClientError)
    def get(self, key: bytes) -> bytes:
        response = self.s3.get_object(Bucket=self.bucket_name, Key=key.decode("utf-8"))
        return response["Body"].read()

    def iter(self) -> Iterator[bytes]:
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket_name):
            for obj in page.get("Contents", []):
                yield obj["Key"].encode("utf-8")

    def len(self) -> int:
        paginator = self.s3.get_paginator("list_objects_v2")
        return sum(
            len(page.get("Contents", []))
            for page in paginator.paginate(Bucket=self.bucket_name)
        )

    def set(self, key: bytes, value: bytes) -> None:
        self.s3.put_object(Bucket=self.bucket_name, Key=key.decode("utf-8"), Body=value)

    def sync(self) -> None:
        # No specific sync operation needed for S3
        pass

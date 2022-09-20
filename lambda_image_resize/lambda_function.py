import json
import boto3
import logging
import bucket_helper
import image_helper
from io import BytesIO
from PIL import Image
import logging
import utils
import os

s3 = boto3.resource("s3")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # src bucket on which we will apply trigger
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    key = f'{event["Records"][0]["s3"]["object"]["key"]}'  # src image/key
    # aws convertes spaces into "+" so remove/revert the changes
    key = key.replace("+", " ")
    print(bucket_name, key)
    print(f"new image {key} inserted in bucket '{bucket_name}'")
    src_bucket = s3.Bucket(bucket_name)
    target_bucket_name = utils.decrypt_secret(os.environ.get('S3_RESIZE_IMG_BUCKET', ""))
    if not target_bucket_name:
        logger.error("Bucket name not configured in environment variable")
        return
    print(target_bucket_name)
    image_helper.image_resize(bucket_name, target_bucket_name, key)
    # response = bucket_helper.copy_to_other_bucket(
    #     src_bucket, target_bucket_name, key)
    # return {
    #     "code": response["code"],
    #     "message": response["message"],
    #     "status_code": response["status_code"],
    # }
    return {
        "code": "Success",
        "message": "Image resized successfully",
        "status_code": 200,
    }

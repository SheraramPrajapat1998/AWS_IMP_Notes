from io import BytesIO
import logging
import os
import boto3
from botocore.exceptions import ClientError
from PIL import Image
# from Pillow import Image

s3 = boto3.resource("s3")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def resize_all_bucket_images(src_bucket_name, dest_bucket_name, width=500, height=500):
    """Resizes all images from source bucket to destination bucket"""
    size = width, height
    bucket = s3.Bucket(src_bucket_name)
    in_mem_file = BytesIO()
    client = boto3.client('s3')

    for key in bucket.objects.all():
        obj = client.get_object(Bucket=src_bucket_name, Key=key.key)
        isimage = obj.get('ContentType', "").startswith("image/")

        if isimage:
            file_byte_string = obj['Body'].read()
            im = Image.open(BytesIO(file_byte_string))

            im.thumbnail(size, Image.ANTIALIAS)
            # ISSUE : https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image
            im.save(in_mem_file, format=im.format)
            in_mem_file.seek(0)
            resized_img_name = f'resized_{key.key}'
            response = client.put_object(
                Body=in_mem_file,
                Bucket=dest_bucket_name,
                Key=resized_img_name
            )
            logger.info(
                f"Image '{key.key}' resized and saved in bucket:'{dest_bucket_name}' with name: '{resized_img_name}'")
        else:
            logger.info(f"Not an image '{key}', escaping...")


def image_resize(src_bucket_name, dest_bucket_name, key, width=500, height=500):
    """Resizes an images from source bucket to destination bucket"""
    size = width, height
    bucket = s3.Bucket(src_bucket_name)
    in_mem_file = BytesIO()
    client = boto3.client('s3')
    obj = client.get_object(Bucket=src_bucket_name, Key=key)
    isimage = obj.get('ContentType', "").startswith("image/")

    if isimage:
        file_byte_string = obj['Body'].read()
        im = Image.open(BytesIO(file_byte_string))

        im.thumbnail(size, Image.ANTIALIAS)
        # ISSUE : https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image
        im.save(in_mem_file, format=im.format)
        in_mem_file.seek(0)
        resized_img_name = f'resized_{key}'

        response = client.put_object(
            Body=in_mem_file,
            Bucket=dest_bucket_name,
            Key=resized_img_name
        )
        logger.info(
            f"Image '{key}' resized and saved in bucket:'{dest_bucket_name}' with name: '{resized_img_name}'")
    else:
        logger.info(f"Not an image '{key}', escaping...")

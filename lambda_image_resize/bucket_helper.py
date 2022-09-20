import os
import sys
import threading
import boto3
import botocore
import logging
from boto3.s3.transfer import TransferConfig

s3 = boto3.resource("s3")
s3_client = boto3.client("s3")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def check_bucket_exists(name):
    """Checks a bucket exists or not."""
    bucket = s3.Bucket(name)
    bucket_exits = True
    try:
        s3.meta.client.head_bucket(Bucket=name)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = e.response['Error']['Code']
        if error_code == '404':
            bucket_exits = False
    return bucket.name if bucket_exits else None


def create_bucket(name, location='ap-south-1'):
    """Creates a bucket in given location"""
    try:
        response = s3.create_bucket(Bucket=name,
                                    CreateBucketConfiguration={
                                        'LocationConstraint': location}
                                    )
        response = {
            "code": "BucketCreated",
            "message": f"Bucket {name} created successfully",
            "status_code": 201
        }
        return response
    except botocore.exceptions.ClientError as e:
        resp = e.response['Error']
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
        logger.info(status_code)
        response = {
            "code": resp['Code'],
            "message": resp['Message'],
            "status_code": status_code
        }
        logger.error(f"ClientError occured due to: {resp}")
        return response
    except Exception as e:
        resp = e.response['Error']
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
        response = {
            "code": resp['Code'],
            "message": resp['Message'],
            "status_code": status_code
        }
        return response


def delete_bucket(name):
    """Deletes a bucket and all objects in it."""
    bucket_exits = check_bucket_exists(name)
    if bucket_exits:
        bucket = s3.Bucket(name)
        for key in bucket.objects.all():
            try:
                key.delete()
                logger.info(f"Deleting key: {key}")
            except botocore.exceptions.ClientError as e:
                resp = e.response['Error']
                status_code = e.response['ResponseMetadata']['HTTPStatusCode']
                logger.info(status_code)
                response = {
                    "code": resp['Code'],
                    "message": resp['Message'],
                    "status_code": status_code
                }
                logger.error(f"ClientError occured due to: {resp}")
                return response
            except Exception as e:
                resp = e.response['Error']
                status_code = e.response['ResponseMetadata']['HTTPStatusCode']
                logger.error("Exception while deleting")
                response = {
                    "code": resp['Code'],
                    "message": resp['Message'],
                    "status_code": status_code
                }
                return response
        bucket.delete()
        logger.info(f"Deleting bucket '{bucket}'")
        response = {
            "code": "BucketDeleted",
                    "message": f"Bucket '{name}' deleted successfully",
                    "status_code": 400
        }
        return response
    else:
        response = {
            "code": "NoSuchBucket",
            "message": f"Bucket '{name}' does not exist",
            "status_code": 404
        }
        logger.error(f"ClientError occured due to: {response}")
        return response


def copy_to_other_bucket(src_bucket, des_bucket_name, key):
    """Copy all objects from src_bucket to destination_bucket"""
    try:
        copy_src = {
            "Bucket": src_bucket.name,
            "Key": key
        }
        bucket = s3.Bucket(des_bucket_name)
        bucket.copy(copy_src, key)
        logger.info(
            f"Copied file '{key}' from bucket '{src_bucket.name}' to bucket '{des_bucket_name}'")
        response = {
            "code": "Success",
            "message": f"Copied file '{key}' to bucket '{des_bucket_name}'",
            "status_code": 200
        }
        return response
    except botocore.exceptions.ClientError as e:
        resp = e.response['Error']
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
        logger.info(status_code)
        response = {
            "code": resp['Code'],
            "message": resp['Message'],
            "status_code": status_code
        }
        logger.error(f"ClientError occured due to: {response}")
        return response
    except Exception as e:
        resp = e.response['Error']
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
        response = {
            "code": resp['Code'],
            "message": resp['Message'],
            "status_code": status_code
        }
        logger.error(f"ClientError occured due to: {response}")
        return response


def file_exists(path):
    return os.path.isfile(path)


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    file_exist = file_exists(file_name)
    if file_exist:
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            s3_client.upload_file(file_name, bucket, object_name)
            logger.info(
                f"File '{file_name}' uploaded successfully to bucket '{bucket}'")
        except botocore.exceptions.ClientError as e:
            logger.error(f"Exception while uploading file '{file_name}'")
            logger.error(f"Traceback: {e}")
            return False
        return True
    else:
        logger.info(f"File '{file_name}' does not exists")


def download_file(bucket_name, key, file_name=None):
    """Download a file to an S3 bucket

    :param bucket_name: Bucket to download file
    :param key: File to download
    :param file_name: Donwload file name. If not specified then S3 object name is used
    :return: True if file was downloaded, else False
    """
    if file_name is None:
        file_name = key
    try:
        s3.Bucket(bucket_name).download_file(key, file_name)
        return True
    except botocore.exceptions.ClientError as e:
        resp = e.response['Error']
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
        logger.info(status_code)
        response = {
            "code": resp['Code'],
            "message": resp['Message'],
            "status_code": status_code
        }
        logger.error(
            f"ClientError occured while downloading file '{file_name}' due to: {response}")
        return False
    except Exception as e:
        resp = e.response['Error']
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
        logger.info(status_code)
        response = {
            "code": resp['Code'],
            "message": resp['Message'],
            "status_code": status_code
        }
        logger.error(
            f"ClientError occured while downloading file '{file_name}' due to: {response}")
        return False


def upload_large_file(file_path, bucket_name, key_path=None):
    """Upload a file to an S3 bucket in multipart

    :param file_path: File to upload file(full file path)
    :param bucket_name: Bucket to upload
    :param key_path: S3 object name. If not specified then file_name is used `Note: if the key_path is not specified then in s3 while uploading it'll create all directories and sub-directories present in path of file`
    :return: True if file was uploaded, else False
    """
    if key_path is None:
        key_path = file_path
    file_exist = file_exists(file_path)
    if file_exist:
        config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                                multipart_chunksize=1024*25, use_threads=True)
        file = file_path
        key = key_path
        s3_client.upload_file(file, bucket_name, key,
                              ExtraArgs={'ACL': 'public-read',
                                         'ContentType': 'video/mp4'},
                              Config=config,
                              Callback=ProgressPercentage(file)
                              )
        logger.info("File '{file_path}' uploaded in '{bucket_name}'")
        return True
    else:
        logger.info("File '{file_path}' does not exist")
        return False


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\n%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


def upload_directory(bucket_name, directory_name):
    pass

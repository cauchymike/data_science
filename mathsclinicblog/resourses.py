import boto3
from mathsclinicblog import app
from flask import session

def _get_s3_resource():
    if app.config["S3_KEY"] and app.config["S3_SECRET"]:
        return boto3.resource(
            's3',
            aws_access_key_id=app.config["S3_KEY"],
            aws_secret_access_key=app.config["S3_SECRET"] 
        )
    else:
        return boto3.resource('s3')


def get_bucket():
    s3_resource = _get_s3_resource()
    if 'bucket' in session:
        bucket = session['bucket']
    else:
        bucket = app.config["S3_BUCKET"]

    return s3_resource.Bucket(bucket)


def get_buckets_list():
    client = boto3.client('s3')
    return client.list_buckets().get('Buckets')

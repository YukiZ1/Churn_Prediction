# Create S3 resource
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import boto3

s3 = boto3.resource('s3')

Glue_asset_bucket = os.getenv('GLUE_ASSET_BUCKET')
glue_script_key = os.getenv('GLUE_SCRIPT_KEY')

# Upload using S3 Object
s3.Object(Glue_asset_bucket, glue_script_key).upload_file('glue_script.py')
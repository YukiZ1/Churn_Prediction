# Create S3 resource
s3 = boto3.resource('s3')

Glue_asset_bucket = 'aws-glue-assets-596603735137-us-east-1'
glue_script_key = 'churn-predict-script/glue_script.py'
# Upload using S3 Object
s3.Object(Glue_asset_bucket, 'churn-predict-script/glue_script.py').upload_file('glue_script.py')
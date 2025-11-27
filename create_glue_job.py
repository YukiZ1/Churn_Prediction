import boto3
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Glue Client
glue = boto3.client('glue', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Configuration from environment variables
Glue_asset_bucket = os.getenv('GLUE_ASSET_BUCKET')
glue_script_key = os.getenv('GLUE_SCRIPT_KEY')
JOB_NAME = os.getenv('JOB_NAME')
ROLE_ARN = os.getenv('GLUE_ROLE_ARN')
SCRIPT_LOCATION = f's3://{Glue_asset_bucket}/{glue_script_key}'
TEMP_DIR = f's3://{Glue_asset_bucket}/tmp/'

# 1. Create the Glue Job (This just defines the job settings)
try:
    glue.create_job(
        Name=JOB_NAME,
        Role=ROLE_ARN,
        Command={
            'Name': 'glueetl',
            'ScriptLocation': SCRIPT_LOCATION,
            'PythonVersion': '3'
        },
        DefaultArguments={
            '--job-language': 'python',
            '--TempDir': TEMP_DIR,
            '--additional-python-modules': 'scikit-learn,pandas,joblib'
        },
        GlueVersion='4.0',
        WorkerType='G.1X',
        NumberOfWorkers=2,
        Timeout=60
    )
    print(f"Job '{JOB_NAME}' created successfully.")
except glue.exceptions.AlreadyExistsException:
    print(f"Job '{JOB_NAME}' already exists. Proceeding to run.")

# 2. Start the Job Immediately (The Run Once logic)
print("Starting job run...")
response = glue.start_job_run(JobName=JOB_NAME)
job_run_id = response['JobRunId']
print(f"Job Run started! ID: {job_run_id}")

# 3. (Optional) Wait for it to finish and print status
# Since start_job_run is asynchronous, the script would normally exit here.
# If you want to wait and see if it succeeded, use this loop:

print("Waiting for job to complete...")
while True:
    status_response = glue.get_job_run(JobName=JOB_NAME, RunId=job_run_id)
    status = status_response['JobRun']['JobRunState']

    if status in ['SUCCEEDED', 'STOPPED', 'FAILED', 'TIMEOUT']:
        print(f"Job finished with status: {status}")

        # If failed, print the error message
        if status == 'FAILED':
            print("Error:", status_response['JobRun']['ErrorMessage'])
        break

    print(f"Status: {status}...")
    time.sleep(30) # Poll every 30 seconds
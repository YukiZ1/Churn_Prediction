# AWS Credentials & Secrets Management Guide

## Overview
This document outlines security best practices for managing AWS credentials and sensitive paths in your project.

## Changes Made

### 1. Environment Variables Setup
- ✅ Created `.env` file (contains your actual credentials - **NEVER commit this**)
- ✅ Created `.env.example` file (template for other developers)
- ✅ Added `.env` to `.gitignore` (already present)

### 2. Updated Files
All Python scripts now use environment variables instead of hardcoded credentials:

- **`create_glue_job.py`** - Uses env vars for AWS region, bucket names, role ARN, and job name
- **`glue_script.py`** - Uses env vars for bucket and model paths
- **`upload_glue_script.py`** - Uses env vars for bucket and script key

### 3. Added Dependency
- Added `python-dotenv>=1.0.0` to `pyproject.toml`

## How to Use

### For Local Development
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual AWS credentials:
  

3. Install dependencies:
   ```bash
   pip install python-dotenv boto3
   ```

4. Run your scripts normally - they'll automatically load from `.env`

### For AWS Glue / Production Deployment
Instead of using `.env` files, use **AWS Secrets Manager** or **IAM Roles**:

#### Option A: AWS Secrets Manager (Recommended)
```python
import boto3
import json

client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='churn-prediction-config')
config = json.loads(secret['SecretString'])
```

#### Option B: IAM Role-based Access (Simpler)
- Attach an IAM role to your Glue job that has necessary S3 permissions
- The Glue job automatically assumes this role
- No credentials needed in code at all!

## Security Best Practices

### ✅ DO:
- Store sensitive data in `.env` files (local development only)
- Use environment variables in your code
- Use AWS Secrets Manager for production
- Use IAM roles for AWS service-to-service authentication
- Add `.env` and `.env.local` to `.gitignore`
- Rotate AWS credentials regularly
- Use minimal IAM permissions (principle of least privilege)
- Enable MFA for AWS accounts
- Use AWS CloudTrail for audit logging

### ❌ DON'T:
- Hardcode credentials in Python files
- Commit `.env` files to git
- Use root AWS account credentials
- Share AWS credentials via email/Slack
- Use same credentials across environments
- Store credentials in version control history

## Checking Git History

If credentials were already committed, you need to:

1. **Rotate your AWS credentials immediately** (they're now public)
2. **Remove from git history**:
   ```bash
   # Using git-filter-repo (recommended)
   pip install git-filter-repo
   git filter-repo --path .env --invert-paths
   ```

3. **Or use BFG Repo-Cleaner**:
   ```bash
   bfg --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_ACCOUNT_ID` | AWS account ID | `123456789` |
| `GLUE_ASSET_BUCKET` | S3 bucket for Glue assets | `aws-glue-assets-123456789-us-east-1` |
| `CHURN_PREDICTION_BUCKET` | S3 bucket for data | `churn-prediction-bucket-...` |
| `GLUE_SCRIPT_KEY` | Path to Glue script in S3 | `churn-predict-script/glue_script.py` |
| `GLUE_ROLE_ARN` | IAM role for Glue | `arn:aws:iam::123456789:role/...` |
| `JOB_NAME` | Glue job name | `churn-prediction-inference-job` |

## Testing Your Setup

```bash
# Test that env vars are loaded correctly
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GLUE_ASSET_BUCKET'))"
```

## Additional Resources
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [python-dotenv Documentation](https://github.com/thixalongo/python-dotenv)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

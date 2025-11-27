# Project Setup Guide for Team Members

## Quick Start

### 1. Clone the Repository
```bash
git clone <repo-url>
cd Churn_Prediction
```

### 2. Setup Environment Variables
```bash
# Copy the template
cp .env.example .env

# Edit .env with your actual AWS credentials
# DO NOT commit this file - it's in .gitignore
```

### 3. Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Or if using uv
uv sync
```

### 4. Verify Setup
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('AWS Region:', os.getenv('AWS_REGION'))"
```

## Environment Variables (.env)

The `.env` file contains your sensitive AWS credentials and should NEVER be committed to git.

**Template (.env.example):**
```
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your_account_id_here
GLUE_ASSET_BUCKET=your-glue-assets-bucket-name
CHURN_PREDICTION_BUCKET=your-churn-prediction-bucket-name
GLUE_SCRIPT_KEY=churn-predict-script/glue_script.py
GLUE_ROLE_ARN=arn:aws:iam::your_account_id:role/AWSGlueServiceRole_churn
JOB_NAME=churn-prediction-inference-job
```

**Your .env file should contain the actual values.**

## Running Scripts

All Python scripts automatically load environment variables from `.env`:

```bash
# Upload Glue script to S3
python upload_glue_script.py

# Create and run Glue job
python create_glue_job.py
```

## ⚠️ Security Reminders

- ✅ `.env` is already in `.gitignore`
- ❌ **NEVER** hardcode credentials in Python files
- ❌ **NEVER** commit `.env` to git
- ✅ Use `python-dotenv` to load credentials at runtime
- ✅ Rotate AWS credentials if they're ever exposed

## AWS Credentials Management

### For Local Development
- Use `.env` file with `python-dotenv` ✅

### For AWS Glue/Production
- Use IAM Roles (recommended - no credentials in code)
- Use AWS Secrets Manager for sensitive data
- Use environment variables set by AWS

## File Structure
```
Churn_Prediction/
├── .env                          # ⚠️ Sensitive - NOT in git
├── .env.example                  # Template for .env
├── .gitignore                    # Includes .env
├── create_glue_job.py           # Uses env vars
├── glue_script.py               # Uses env vars
├── upload_glue_script.py        # Uses env vars
├── SECURITY.md                  # This guide
└── pyproject.toml               # Includes python-dotenv
```

## Troubleshooting

### `.env` file not loading?
```bash
# Verify python-dotenv is installed
pip install python-dotenv

# Check .env file exists in project root
ls -la .env
```

### Getting "Cannot find AWS credentials" error?
- Ensure `.env` file exists in the project root
- Check that `.env` contains all required variables
- Run: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('AWS_REGION'))"`

### Accidentally committed credentials?
Immediately:
1. Rotate your AWS credentials in AWS Console
2. Contact the team lead
3. Use git history cleanup tools (see SECURITY.md)

## Questions?

See `docs/README_SECURITY.md` for detailed information about credential management and best practices.

# Telco Customer Churn: Scalable Batch Inference Pipeline on AWS
## Project Overview
This project implements an end-to-end MLOps workflow for predicting customer churn at scale. Unlike standard local modeling, this architecture decouples model training from inference, utilizing AWS Glue (Apache Spark) to perform distributed batch predictions on raw data stored in Amazon S3.

The system is designed to handle high-volume data ingestion (e.g., daily logs from multiple districts), enabling automated, serverless inference without managing underlying infrastructure.

## Tech Stack
Cloud & Storage: AWS S3, AWS Glue (Serverless ETL)

Data Processing: PySpark, Pandas (via Apache Arrow)

Machine Learning: Scikit-Learn, Joblib

DevOps/SDK: Python Boto3 (Infrastructure as Code)

## System Architecture
1. Model Training (Local): A Scikit-Learn pipeline is trained and serialized (.joblib) to S3.

2. Infrastructure Provisioning: Python scripts use boto3 to programmatically create and configure AWS Glue Jobs.

3. Distributed Inference (Cloud):

Spark reads partitioned CSV data from S3.

Spark broadcasts the serialized model to worker nodes.

mapInPandas (Pandas UDF) handles vectorized inference, bridging Spark and Scikit-Learn.

Results (Probabilities + Class predictions) are written back to a Data Lake (S3).

## File Structure & Usage
1. Model Development & Artifact Management
`ML_engineering_workflow.ipynb`

Develops the Scikit-Learn pipeline (Preprocessing + Classifier).

Handles model serialization using joblib.

Uploads the trained model artifact to a dedicated S3 bucket (s3://.../models/).

2. The ETL & Inference Engine
`glue_script.py`

Role: The entry point for the AWS Glue Spark job.

Key Technical Implementation:

Downloads the model artifact to the Spark driver/executors.

Defines a custom inference function using @pandas_udf / mapInPandas for efficient memory management.

Performs probability calculation (predict_proba) and applies a custom decision threshold (e.g., >0.6).

Writes results to S3 partitioned by processing_date.

3. Infrastructure as Code (IaC)
`upload_glue_script.py`

Uploads the ETL script to the S3 script repository.

`create_glue_job.py`

Uses the AWS Boto3 SDK to programmatically define the Glue Job.

Configures worker types (G.1X), timeout settings, and installs required dependencies (scikit-learn, pandas) on the cluster.

Triggers the job execution via API (removing the need for manual console interaction).

## How to Run
1. Configure AWS credentials locally.
2. Run ML_engineering_workflow.ipynb to train and upload the model.
3. Run upload_glue_script.py to deploy the Spark logic.
4. Run create_glue_job.py to provision infrastructure and execute the batch inference.
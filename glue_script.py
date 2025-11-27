import boto3
import joblib
import pandas as pd
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
from pyspark.sql.functions import current_date
from io import BytesIO

# --- CONFIGURATION ---
BUCKET = 'churn-prediction-bucket-91645758-7495-485b-9f19-413d2acdfb02'
MODEL_KEY = 'models/churn_prediction_pipeline.joblib'
INPUT_DATA_PATH = f's3://{BUCKET}/raw-input/'
OUTPUT_DATA_PATH = f's3://{BUCKET}/pred_output/'
LOCAL_MODEL_PATH = '/tmp/model.joblib'
THRESHOLD = 0.5

# 1. Initialize Spark
sc = SparkContext()
spark = SparkSession(sc)

# 2. Download Model from S3 to Local Driver/Worker
# Note: In Glue, we download to /tmp/ which is accessible
s3 = boto3.client('s3')
obj = s3.get_object(Bucket=BUCKET, Key=MODEL_KEY)
pipe = joblib.load(BytesIO(obj['Body'].read()))

# Broadcast the model path so all workers know where to look (or download on every worker)
# Ideally, for massive scale, you download inside the UDF, but for standard Glue usage:
# We will load the model inside the UDF to ensure it exists on the executor memory.

# 3. Define the Inference Function (The "Pandas" part)
# This function receives an ITERATOR of DataFrames.
# Spark handles the memory management behind the scenes.
def get_inference_results(iterator):
    
    for pdf in iterator:
        # 'pdf' is a standard pandas.DataFrame!
        # drop null rows, extract id column
        pdf['TotalCharges'] = pd.to_numeric(pdf.TotalCharges, errors='coerce')
        pdf['TotalCharges'] = pdf['TotalCharges'].fillna(pdf['TotalCharges'].mean())
        pdf = pdf.drop(labels=pdf[pdf['tenure'] == 0].index, axis=0)
        id_list = pdf['customerID'].values

        # use pipeline to do predict task
        y_prob = pipe.predict_proba(pdf)[:,1]
        y_pred = (y_prob >= THRESHOLD).astype(int)
        
        # Construct Output DataFrame
        # We perform the "Select" logic here in Python
        result_pdf = pd.DataFrame({
            'userid': id_list,           # Keep User ID
            'prediction_proba': y_prob, # The float probability
            'prediction': y_pred          # The 0/1 integer
        })
        
        yield result_pdf


# 4. Define Output Schema
# This must match the DataFrame yielded in step D above
schema = StructType([
    StructField("userid", StringType()),
    StructField("prediction_proba", DoubleType()),
    StructField("prediction", IntegerType())
])

# 5. Read Raw Data
df_raw = spark.read.option("header", "true").csv(INPUT_DATA_PATH)

# 6. Apply Inference
# This returns a dataframe with ONLY: userid, prediction_proba, prediction
df_scored = df_raw.mapInPandas(get_inference_results, schema=schema)

# 7. Add Date Column
# It is more efficient to add the date using Spark than inside the Python loop
final_output = df_scored.withColumn("processing_date", current_date())

# 8. Write to S3
# Note: You cannot "append" to a single CSV file in S3 (S3 is object storage).
# You write a NEW file into the output folder.
final_output.write.mode("append").partitionBy("processing_date").csv(OUTPUT_DATA_PATH)

print("Inference complete.")
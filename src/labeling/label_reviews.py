import gc
from typing import Iterator
import pandas as pd
from bertopic import BERTopic
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType

MODEL_PATH = "/home/cs179g/repo/data/BERTopicModel"
INPUT_PARQUET = "/home/cs179g/repo/data/clean_reviews.parquet"
OUTPUT_PARQUET = "/home/cs179g/repo/data/labeled_reviews.parquet"

# build spark session
spark = (
    SparkSession.builder
    .appName("Phase2")
    .config("spark.driver.memory", "8g")
    .config("spark.executor.memory", "8g")
    # trying to avoid crashing
    .config("spark.sql.debug.maxToStringFields", "100")
    .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    .config("spark.sql.execution.arrow.maxRecordsPerBatch", "4096")
    # prevent loading duplicate models
    .config("spark.task.cpus", "2")
    .getOrCreate()
)

driver_model = BERTopic.load(MODEL_PATH)
topic_info_pd = driver_model.get_topic_info()[["Topic", "Name"]]
# clean up after getting info
del driver_model
gc.collect()

topic_lookup_df = (
    spark.createDataFrame(topic_info_pd)
    .withColumnRenamed("Topic", "topic_id")
    .withColumnRenamed("Name", "topic_name")
)

# load reviews
review_df = (
    spark.read.parquet(INPUT_PARQUET)
    .withColumn("clean_text", F.coalesce(F.col("clean_text"), F.lit("")))
)

# define output schema
output_schema = StructType(
    list(review_df.schema.fields) + [
        StructField("topic_id", IntegerType(), True),
        StructField("topic_prob", FloatType(), True),
    ])

# the big thing
# uses iterators and partitions to process the large review set in batches
def assign_topics(iterator: Iterator[pd.DataFrame]) -> Iterator[pd.DataFrame]:
    # load once
    model = BERTopic.load(MODEL_PATH)
    
    for pdf in iterator:
        if pdf.empty:
            continue
            
        docs = pdf["clean_text"].astype(str).tolist()
        topics, probs = model.transform(docs)

        # we explicitly pass the type to avoid a schema mismatch error from pandas
        pdf["topic_id"] = pd.Series(topics, index=pdf.index, dtype="int32")
        pdf["topic_id"] = np.asarray(topics, dtype="int32")
        pdf["topic_prob"] = probs.astype("float32")
            
        yield pdf


labeled_df = (
    review_df
    .mapInPandas(assign_topics, schema=output_schema)
    .join(F.broadcast(topic_lookup_df), on="topic_id", how="left")
)


labeled_df.write.mode("overwrite").parquet(OUTPUT_PARQUET)
print("Successfully saved labeled reviews to:", OUTPUT_PARQUET)
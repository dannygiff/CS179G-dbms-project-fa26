import sys
import time
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

MASTER = sys.argv[1]
DATA_PATH = sys.argv[2]
RESULTS_PATH = "data/benchmark_results.csv"

# .master(MASTER) tells spark how many cores to use (local[1] - local[4] in our case)
# https://spark.apache.org/docs/latest/submitting-applications.html#master-urls
spark = SparkSession.builder.master(MASTER).config("spark.driver.memory", "8g").appName("benchmark").getOrCreate()

start = time.perf_counter()

df = spark.read.json(DATA_PATH)

# cleaning steps form "datacleaner.py"
clean_df = (
    df
    .filter((F.col("language") == "english") & F.col("review").isNotNull())
    .withColumn("clean_text", F.btrim(F.col("review")))
    .filter(F.length("clean_text") > 0)
    .withColumn("raw_word_count", F.size(F.split(F.col("clean_text"), r"\s+")))
    .withColumn("post_review_playtime", F.greatest(F.lit(0), F.col("author.playtime_forever") - F.col("author.playtime_at_review")))
    .withColumn("timestamp_formatted", F.from_unixtime(F.col("timestamp_created"), "yyyy-MM-dd"))
)

# groupBy forces a shuffle, spark has to then move rows between cores (essentially just creating work)
# https://github.com/apache/spark/blob/master/sql/catalyst/src/main/scala/org/apache/spark/sql/catalyst/optimizer/Optimizer.scala
# line 1506
result = (
    clean_df
    .groupBy("voted_up")
    .agg(F.count("*").alias("reviews"), F.avg("raw_word_count").alias("avg_words"), F.avg("post_review_playtime").alias("avg_post_playtime"))
    .collect()
)

elapsed = time.perf_counter() - start

print(f"{MASTER} {DATA_PATH}: {elapsed:.2f} seconds, result: {result}")

# first run with nonexistent file will need to add columns
if not os.path.exists(RESULTS_PATH):
    with open(RESULTS_PATH, "w") as f:
        f.write("master,data_path,seconds\n")

# append rows into the file
with open(RESULTS_PATH, "a") as f:
    f.write(f"{MASTER},{DATA_PATH},{elapsed:.2f}\n")

spark.stop()
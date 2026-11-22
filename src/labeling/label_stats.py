from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("VerifyOutput").getOrCreate()
df = spark.read.parquet("/home/cs179g/repo/data/labeled_reviews.parquet")

print("Total rows:", df.count())
df.select("clean_text", "topic_id", "topic_prob", "topic_name").show(10, truncate=60)
df.groupBy("topic_id", "topic_name").count().orderBy("count", ascending=False).show(25, truncate=False)
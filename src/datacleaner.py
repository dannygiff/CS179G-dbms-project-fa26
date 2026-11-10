from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# data_path = "./data/over_100k_games_reviews.json"
data_path = "./data/data_v2.json"

spark = (
  SparkSession.builder
  .appName("Phase2")
  .config("spark.driver.memory", "8g")
  .config("spark.executor.memory", "8g")
  .config("spark.sql.debug.maxToStringFields", "100")
  .getOrCreate()
)

raw_df = spark.read.option("multiLine", True).option("mode", "PERMISSIVE")\
  .format("json").load(data_path)\
  # .withColumn("app_id", F.regexp_extract(F.col("_corrupt_record"),r'"app_id":([0-9]+)', 1))

exploded_response_df = raw_df.withColumn('response',F.explode(F.col("response"))).select("*", "response.*").drop("response").repartition(4)
# response_df = df.groupBy("app_id").pivot("response.key").agg(F.first("response.val"))

flat_df = exploded_response_df.select(
  "app_id",
  "recommendationid",
  # F.col("author.deck_playtime_at_review").alias("deck_playtime_at_review"),
  F.col("author.last_played").alias("last_played"),
  F.col("author.num_reviews").alias("author_num_reviews"),
  F.col("author.playtime_forever").alias("playtime_forever"),
  F.col("author.playtime_at_review").alias("playtime_at_review"),
  F.col("author.playtime_last_two_weeks").alias("playtime_last_two_weeks"),
  F.col("author.steamid").alias("steamid"),
  "language",
  "comment_count",
  "steam_purchase",
  # "primarily_steam_deck",
  "received_for_free",
  "refunded",
  "review",
  "voted_up",
  "votes_up",
  "votes_funny",
  "weighted_vote_score",
  F.col("developer_response").isNotNull().alias("has_dev_reponse"),
  "written_during_early_access",
  "timestamp_created",
  "timestamp_updated",
  F.col("hardware").isNotNull().alias("has_hardware"),
  F.col("hardware.adapter_description").alias("adapter_description"),
  F.col("hardware.cpu_name").alias("cpu_name"),
  F.col("hardware.os").alias("os"),
  F.col("hardware.system_ram").alias("system_ram"),
  F.col("hardware.vram_size").alias("vram_size"),
).cache()

# raw_df.printSchema()
flat_df.show(5)
flat_df.printSchema()
flat_df.groupBy("app_id").count().orderBy("app_id").show(truncate=False)
total_count = flat_df.groupBy("app_id").count().select("count").agg(F.sum("count")).collect()[0][0]
print(f"Total: {total_count}")
# df.cache().filter(F.col("_corrupt_record").isNotNull()).select("_corrupt_record").show(20)
# print((df.count()), len(df.columns()))

clean_df = (
  flat_df
  .filter((F.col("language") == "english") & F.col("review").isNotNull())
  .withColumn("clean_text", F.btrim(F.col("review")))
  .filter(F.length("clean_text") > 0)
  .withColumn("raw_word_count", F.size(F.split(F.col("clean_text"), r"\s+")))
  .withColumn("post_review_playtime", F.greatest(F.lit(0), F.col("playtime_forever") - F.col("playtime_at_review")))
  .withColumn("timestamp_formatted", F.from_unixtime(F.col("timestamp_created"), "yyyy-MM-dd"))
)
clean_df.write.mode("overwrite").parquet("./data/clean_reviews.parquet")

clean_df.groupBy("app_id").count().orderBy("count").show(truncate=False)
print(f"Total clean reviews: {clean_df.count()}")
has_up = F.col("votes_up") > 0
has_funny = F.col("votes_funny") > 0
has_shifted_score = F.col("weighted_vote_score") != 0.5
has_any_vote = has_up | has_funny | has_shifted_score

usable_reviews = (
  clean_df
  .groupBy("app_id")
  .agg(
    F.count("*").alias("Total reviews"),
    F.sum(F.when(has_any_vote, 1).otherwise(0)).alias("Nonzero votes reviews"),
    F.round((F.sum(F.when(has_any_vote, 1).otherwise(0)) / F.count("*")) * 100, 2).alias(f"% usable of total")
  )
)
usable_reviews.orderBy("% usable of total").show()
total_usable = usable_reviews.agg(F.sum('Nonzero votes reviews')).collect()[0][0]
print(f"Total usable (for training): {total_usable} out of {total_count} ({round((total_usable/total_count) * 100, 2)}%)")
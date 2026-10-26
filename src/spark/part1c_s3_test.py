from pathlib import Path
from pyspark.sql import SparkSession

csv_path = Path(__file__).parent / "test.csv"

spark = SparkSession.builder.appName("part1c").getOrCreate()

df = spark.read.csv(str(csv_path), header=True, inferSchema=True)

# print(df.filter(df.zipcode == 78727).count())

df.createOrReplaceTempView("people")
spark.sql("SELECT COUNT(*) AS people_in_78727 FROM people WHERE zipcode = 78727").show()
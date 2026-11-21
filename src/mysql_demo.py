from pyspark.sql import SparkSession
import mysql.connector

# 1. Create Spark session
spark = SparkSession.builder \
    .appName("SparkMySQLExample") \
    .master("local[2]") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# 2. Create sample data
data = [
    (1, "Alice", 22),
    (2, "Bob", 19),
    (3, "Charlie", 25),
    (4, "David", 20),
    (5, "Emma", 24)
]
columns = ["id", "name", "age"]
df = spark.createDataFrame(data, columns)
print("Original Data:")
df.show()

# 3. Process data using PySpark
filtered_df = df.filter(df.age > 21)
print("Filtered Data:")
filtered_df.show()

# 4. Save Spark results to MySQL
jdbc_url = "jdbc:mysql://127.0.0.1:3306/university"
properties = {
    "user": "root",
    "driver": "com.mysql.cj.jdbc.Driver"
}
filtered_df.write.jdbc(
    url=jdbc_url,
    table="filtered_students",
    mode="overwrite",
    properties=properties
)
print("Successfully saved results to MySQL!")

# 5. Retrieve results using Python
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    database="university"
)
cursor = conn.cursor()
cursor.execute(
    "SELECT * FROM filtered_students ORDER BY id"
)
print("Data retrieved from MySQL:")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()

# 6. Stop Spark
spark.stop()
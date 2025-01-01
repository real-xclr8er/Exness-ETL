from pyspark.sql import SparkSession

# Initialize SparkSession with increased memory
spark = SparkSession.builder \
    .appName("DBTest") \
    .config("spark.jars", "/opt/spark/jars/postgresql-42.6.2.jar") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.extraClassPath", "/opt/spark/jars/postgresql-42.6.2.jar") \
    .config("spark.driver.extraClassPath", "/opt/spark/jars/postgresql-42.6.2.jar") \
    .getOrCreate()

# JDBC URL for TimescaleDB
jdbc_url = "jdbc:postgresql://market_data_db:5432/market_data"
db_properties = {
    "user": "market_collector",
    "password": "1331",
    "driver": "org.postgresql.Driver"
}

# Query only a subset of the table to limit data
query = "(SELECT * FROM tick_data LIMIT 1000) AS subset"

try:
    # Read the subset of data
    df = spark.read.jdbc(url=jdbc_url, table=query, properties=db_properties)
    df.show(10)  # Display the first 10 rows
    print("Database connection successful!")
except Exception as e:
    print("Failed to connect to the database:", e)

# Stop Spark session
spark.stop()

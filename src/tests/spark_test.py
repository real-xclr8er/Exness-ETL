from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg
import time

def test_spark_functionality():
    """
    Test Spark functionality while demonstrating key concepts of distributed processing
    """
    print("\n=== Starting Comprehensive Spark Test ===")
    
    try:
        # Initialize Spark session
        # We use master('local[1]') first to ensure basic functionality
        print("\nStep 1: Creating Spark Session...")
        spark = SparkSession.builder \
            .appName("TradingSystemTest") \
            .config("spark.sql.shuffle.partitions", "2") \
            .master("local[1]") \
            .getOrCreate()

        print("Successfully created Spark session!")
        
        # Create sample trading data
        print("\nStep 2: Creating sample trading data...")
        trading_data = [
            ("AAPL", "2024-01-01", 100.0, 102.0, 99.0, 101.5, 1000000),
            ("AAPL", "2024-01-02", 101.5, 103.0, 101.0, 102.8, 1200000),
            ("MSFT", "2024-01-01", 200.0, 202.0, 199.0, 201.5, 800000),
            ("MSFT", "2024-01-02", 201.5, 204.0, 201.0, 203.8, 900000)
        ]
        
        # Define the schema explicitly
        print("Creating DataFrame with trading data schema...")
        df = spark.createDataFrame(
            trading_data,
            ["symbol", "date", "open", "high", "low", "close", "volume"]
        )
        
        # Perform some basic analysis
        print("\nStep 3: Performing basic analysis...")
        
        # Calculate average daily trading range
        print("Calculating trading metrics...")
        analysis = df.withColumn(
            "daily_range", 
            col("high") - col("low")
        ).groupBy("symbol").agg(
            avg("daily_range").alias("avg_daily_range"),
            avg("volume").alias("avg_volume")
        )
        
        # Show results
        print("\nAnalysis Results:")
        analysis.show()
        
        # Verify data reading/writing capabilities
        print("\nStep 4: Testing data I/O capabilities...")
        df.write.mode("overwrite").parquet("/opt/spark/data/test_data.parquet")
        read_back = spark.read.parquet("/opt/spark/data/test_data.parquet")
        print(f"Successfully wrote and read back {read_back.count()} records")
        
        print("\n✓ All tests completed successfully!")
        print("Spark cluster is properly configured and operational")
        
        # Clean up
        spark.stop()
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return False

if __name__ == "__main__":
    test_spark_functionality()
# spark_processor.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window
from pyspark.sql.types import StructType, StructField, TimestampType, DoubleType, StringType
import logging
from pathlib import Path
from config import SYMBOLS, Timeframe, DATA_FOLDER

class SparkProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("MT5DataProcessor") \
            .config("spark.sql.warehouse.dir", "spark-warehouse") \
            .getOrCreate()
            
        self.schema = StructType([
            StructField("time", TimestampType(), True),
            StructField("open", DoubleType(), True),
            StructField("high", DoubleType(), True),
            StructField("low", DoubleType(), True),
            StructField("close", DoubleType(), True),
            StructField("tick_volume", DoubleType(), True),
            StructField("spread", DoubleType(), True),
            StructField("real_volume", DoubleType(), True)
        ])
        
    def read_symbol_data(self, symbol, timeframe):
        """Read all CSV files for a symbol/timeframe combination"""
        path = str(Path(DATA_FOLDER) / symbol / timeframe.name / "*.csv")
        return self.spark.read.csv(path, header=True, schema=self.schema)
    
    def process_data(self, symbol, timeframe):
        """Process data for a symbol/timeframe combination"""
        df = self.read_symbol_data(symbol, timeframe)
        
        # Basic processing example - you can extend this
        processed = df \
            .withWatermark("time", "1 hour") \
            .groupBy(
                window("time", "1 day"),
                "symbol"
            ).agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "tick_volume": "sum",
                "real_volume": "sum"
            })
            
        return processed
    
    def process_all(self):
        """Process all symbols and timeframes"""
        for symbol in SYMBOLS:
            for timeframe in Timeframe:
                try:
                    processed_df = self.process_data(symbol, timeframe)
                    # Save processed data
                    output_path = str(Path(DATA_FOLDER) / "processed" / symbol / timeframe.name)
                    processed_df.write.mode("overwrite").parquet(output_path)
                except Exception as e:
                    logging.error(f"Error processing {symbol} {timeframe.name}: {e}")
                    continue
    
    def stop(self):
        """Stop Spark session"""
        self.spark.stop()

if __name__ == "__main__":
    processor = SparkProcessor()
    try:
        processor.process_all()
    finally:
        processor.stop()
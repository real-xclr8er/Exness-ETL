# spark_setup.ps1

# Download Spark if not exists
$SPARK_VERSION = "3.5.0"
$HADOOP_VERSION = "3"
$SPARK_DIR = ".\spark"

if (-not (Test-Path $SPARK_DIR)) {
    Write-Host "Downloading Spark..."
    $sparkUrl = "https://dlcdn.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz"
    $outputFile = "spark.tgz"
    
    Invoke-WebRequest -Uri $sparkUrl -OutFile $outputFile
    tar -xzf $outputFile
    Move-Item "spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION" $SPARK_DIR
    Remove-Item $outputFile
}

# Set environment variables
$env:SPARK_HOME = (Resolve-Path $SPARK_DIR).Path
$env:PATH = "$env:SPARK_HOME\bin;$env:PATH"
$env:PYTHONPATH = "$env:SPARK_HOME\python;$env:PYTHONPATH"

# Test Spark installation
python -c "from pyspark.sql import SparkSession; print('Spark installation successful')"
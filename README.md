# Trading System Project

## Project Overview
A Windows-based algorithmic trading system integrating MetaTrader 5 with distributed data processing capabilities using Apache Spark.

## Current Status
- ✓ Basic project structure established
- ✓ Spark cluster configuration completed
- ✓ Docker environment configured and tested
- ✓ Basic data processing pipeline verified

## Environment Setup
### Prerequisites
- Windows 11
- Docker Desktop
- Python 3.10+
- MetaTrader 5
- PowerShell 7+

### Components
- Apache Spark 3.4.0 cluster (1 master, 1 worker)
- Python environment with PySpark
- Docker containers for distributed processing

## Directory Structure
```
trading_system/
├── docker/
│   ├── Dockerfile.spark
│   └── docker-compose.yml
├── src/
│   └── utils/
│       └── spark_test.py
├── data/
│   ├── raw/
│   └── processed/
└── configs/
    └── spark-defaults.conf
```

## Setup Instructions
1. Clone the repository
2. Navigate to the docker directory
3. Run `docker-compose up -d --build`
4. Verify setup by running the test script:
   ```powershell
   docker exec -it spark-master python3 /opt/spark/src/utils/spark_test.py
   ```

## Next Steps
1. Implement MT5 data collection pipeline
2. Set up real-time data processing
3. Develop analysis modules
4. Create visualization components
5. Implement trading strategies

## Development Guidelines
- Use virtual environments for Python development
- Follow PEP 8 coding standards
- Document all functions and modules
- Maintain test coverage for new features
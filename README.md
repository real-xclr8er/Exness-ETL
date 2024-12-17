# Trading System Project

## Project Overview
A Windows-based algorithmic trading system integrating MetaTrader 5 with distributed data processing capabilities. The system features real-time tick data collection and efficient data storage for future AI/ML applications.

## Current Status
- ✓ Basic project structure established
- ✓ Spark cluster configuration completed
- ✓ Docker environment configured and tested
- ✓ Basic data processing pipeline verified
- ✓ Real-time tick data collection implemented
- ✓ Efficient Parquet storage system established
- ✓ Multi-threaded data collection with error handling
- ✓ Background process capability with system tray interface

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
- Real-time tick data collector
- Parquet-based storage system

## Directory Structure
```
trading_system/
├── docker/
│   ├── Dockerfile.spark
│   └── docker-compose.yml
├── src/
│   ├── collectors/
│   │   └── tick_collector.py
│   ├── processors/
│   │   └── price_processor.py
│   └── utils/
│       ├── cleanup.py
│       ├── spark_test.py
│       └── timeframe_tester.py
├── scripts/
│   └── build_executable.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── ticks/
└── configs/
    └── spark-defaults.conf
```

## Setup Instructions
1. Clone the repository
2. Create and activate Python virtual environment
3. Install required packages: `pip install -r requirements.txt`
4. For Docker components:
   - Navigate to the docker directory
   - Run `docker-compose up -d --build`
5. Configure MetaTrader 5 credentials (see documentation)
6. Run the tick collector:
   - As a script: `python src/collectors/tick_collector.py`
   - Or build executable: `python scripts/build_executable.py`

## Features
### Data Collection
- Real-time tick data collection for multiple symbols
- Efficient multi-threaded processing
- Automatic error recovery and logging
- Parquet file storage with compression
- System tray interface for background operation

### Data Processing
- Timeframe availability testing
- Data validation and cleanup utilities
- Price processing capabilities
- Integration with Spark for distributed processing

## Next Steps
### Planned Features
1. Hybrid Storage Solution
   - SQLite database for metadata tracking
   - Data completeness monitoring
   - Gap detection and recovery
   - Collection statistics

2. Enhanced Monitoring
   - Real-time collection statistics
   - Data quality reporting
   - Alert system for collection issues
   - Visualization tools

3. System Improvements
   - Configuration file support
   - Network resilience features
   - Data compression optimization
   - API endpoints for external systems

4. Integration Features
   - Data export utilities
   - Streaming capabilities
   - Custom symbol list support
   - AI/ML pipeline integration

## Development Guidelines
- Use virtual environments for Python development
- Follow PEP 8 coding standards
- Document all functions and modules
- Maintain test coverage for new features
- Use Git for version control
- Keep data collection and processing separate
- Implement proper error handling and logging
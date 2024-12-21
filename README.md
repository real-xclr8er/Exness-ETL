# Trading System Project

## Project Overview
A Windows-based algorithmic trading system integrating MetaTrader 5 with distributed data processing capabilities. The system features real-time tick data collection, efficient data storage, and database integration for future AI/ML applications.

## Current Status
- ✓ Basic project structure established
- ✓ Spark cluster configuration completed
- ✓ Docker environment configured and tested
- ✓ Real-time tick data collection implemented
- ✓ Efficient Parquet and PostgreSQL hybrid storage system established
- ✓ Database deduplication and integrity mechanisms in place
- ✓ Background process capability with system tray interface

## Environment Setup
### Prerequisites
- Windows 11
- Docker Desktop
- Python 3.10+
- MetaTrader 5 installed
- PowerShell 7+

### Components
- TimescaleDB with deduplication and schema validation
- Apache Spark 3.4.0 cluster (1 master, 1 worker)
- Python environment with data processing scripts
- Dockerized architecture for portability
- Real-time tick data collection with Parquet and PostgreSQL integration

## Directory Structure
```
trading_system/
├── docker/
│   ├── Dockerfile.timescaledb
│   ├── docker-compose.timescaledb.yml
│   ├── config/
│   │   └── pg_hba.conf
│   ├── init-scripts/
│   │   └── 01-init-tables.sql
│   ├── network-setup.yml
├── scripts/
│   ├── fetch_historical_data.py
│   ├── verify_tick_data.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── ticks/
└── mt5_available_fields.txt
```

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/trading_system.git
cd trading_system
```

### Step 2: Build and Run Docker Containers
1. Navigate to the Docker directory:
   ```bash
   cd docker
   ```
2. Start the PostgreSQL container:
   ```bash
   docker-compose -f docker-compose.timescaledb.yml up -d --build
   ```
3. Initialize the database schema:
   ```bash
   docker cp init-scripts/01-init-tables.sql market_data_db:/tmp/01-init-tables.sql
   docker exec -it market_data_db psql -U market_collector -d market_data -f /tmp/01-init-tables.sql
   ```

### Step 3: Configure MetaTrader 5
Ensure your MetaTrader 5 terminal is running and accessible by the Python scripts.

### Step 4: Run Data Collection Scripts
1. Verify tick data availability:
   ```bash
   python scripts/verify_tick_data.py
   ```
2. Fetch historical tick data:
   ```bash
   python scripts/fetch_historical_data.py
   ```

## Features
### Data Collection
- Real-time and historical tick data collection
- Supports multiple symbols:
  ```python
  SYMBOLS = [
      'AUDUSD', 'BTCJPY', 'CHFJPY', 'EURUSD', 'GBPJPY',
      'US30', 'USDJPY', 'USTEC', 'XAUUSD', 'BTCUSD'
  ]
  ```
- Deduplication and integrity checks during data insertion

### Data Processing
- Parquet and PostgreSQL hybrid storage
- Database-level unique constraints to prevent duplicates
- Efficient timestamp-based querying for incremental updates

## Next Steps
1. Implement real-time tick data streaming.
2. Add AI/ML pipeline integration.
3. Enhance monitoring and visualization features.

## Development Guidelines
- Use virtual environments for Python development
- Follow PEP 8 coding standards
- Document all functions and modules
- Maintain test coverage for new features
- Use Git for version control
- Keep sensitive data out of version control
- Ensure database and storage systems are clean and deduplicated


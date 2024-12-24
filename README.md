# Trading System Project

## Project Overview
This Windows-based algorithmic trading system integrates TimescaleDB, Spark, and MetaTrader 5 to handle historical and real-time financial tick data. The system is designed for flexibility, scalability, and integration with analytics tools, saving data to both a database and Parquet files for efficient processing and ensuring data consistency.

## Current Status
- ✓ Basic project structure established
- ✓ Spark cluster configuration completed
- ✓ Docker environment configured and tested
- ✓ Real-time tick data collection implemented
- ✓ Efficient Parquet and TimescaleDB hybrid storage system established
- ✓ Database deduplication and integrity mechanisms in place

## Current Features

### Database
- **Database Engine**: TimescaleDB
- **Configuration**: Optimized for time-series data storage
- **Status**:
  - Historical tick data available for:
    - AUDUSD, BTCJPY, CHFJPY, EURUSD, GBPJPY, US30, USDJPY, USTEC, XAUUSD, BTCUSD
  - Robust deduplication mechanisms
  - Continuous data collection with graceful interruption handling

### Data Collection

#### Historical Data Handling
- **Script**: `fetch_historical_data.py`
  - Fetches historical tick data from MetaTrader 5
  - Ensures deduplication during database inserts via `ON CONFLICT DO NOTHING`
  - Resumes from the last recorded tick
  - Saves data to TimescaleDB

#### Real-Time Tick Collection
- **Script**: `tick_collector.py`
  - Collects live tick data
  - Appends to both TimescaleDB and Parquet files
  - Ensures continuity from the last tick in the database
  - Maintains consistent Parquet file structure

### Storage Architecture

#### Parquet Files
- Directory structure: `data/ticks/{SYMBOL}/{YYYYMMDD}.parquet`
- Optimized for bulk analytics and ML workflows

#### TimescaleDB
- Deduplicates and stores data for real-time querying
- Optimized for time-series operations
- Supports complex analytics queries

### Data Integrity
- **Deduplication**: Prevents duplicates in both database and Parquet files
- **Continuity**: Automatic resumption from last recorded tick
- **Validation**: Built-in data verification tools

### Docker Configuration
- **Dockerized Components**:
  - TimescaleDB database
  - Spark environment for data processing
- **Configuration Files**:
  - `Dockerfile.timescaledb`: Custom TimescaleDB image
  - `docker-compose.timescaledb.yml`: Database orchestration
  - `docker-compose.spark.yml`: Spark environment setup

## Setup Instructions

### Prerequisites
- Windows 11
- Docker Desktop
- MetaTrader 5 terminal configured for your broker
- Python 3.10+ with required dependencies:
  - `pyarrow`
  - `pandas`
  - `sqlalchemy`
- PowerShell 7+

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

### Installation Steps

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```

2. **Start Infrastructure**
```bash
# Start TimescaleDB
docker-compose -f docker/docker-compose.timescaledb.yml up -d --build

# Initialize database schema
docker cp init-scripts/01-init-tables.sql market_data_db:/tmp/01-init-tables.sql
docker exec -it market_data_db psql -U market_collector -d market_data -f /tmp/01-init-tables.sql

# Start Spark (Optional for data aggregation)
docker-compose -f docker/docker-compose.spark.yml up -d --build
```

3. **Initialize Data Collection**
```bash
# Fetch historical data
python scripts/fetch_historical_data.py

# Start real-time collection
python src/collectors/tick_collector.py
```

### Database Management

#### Connecting to TimescaleDB
```bash
docker exec -it market_data_db psql -U market_collector -d market_data
```

#### Common Database Queries
```sql
-- Count total rows
SELECT COUNT(*) FROM market_data.tick_data;

-- View data range by symbol
SELECT symbol,
       MIN(tick_time) AS first_tick,
       MAX(tick_time) AS last_tick
FROM market_data.tick_data
GROUP BY symbol;

-- Check for duplicates
SELECT symbol, tick_time, COUNT(*)
FROM market_data.tick_data
GROUP BY symbol, tick_time
HAVING COUNT(*) > 1;
```

## Data Verification
- **Script**: `verify_tick_data.py`
  - Validates database data integrity
  - Provides sample outputs for inspection
  - Checks for data continuity

## Next Steps

1. **Spark Integration**
   - Verify TimescaleDB and Parquet file interaction
   - Implement data aggregation jobs
   - Set up analytics pipelines

2. **Data Aggregation**
   - Generate candlestick data (1-minute, 5-minute intervals)
   - Implement real-time aggregation pipelines

3. **AI/ML Integration**
   - Define feature extraction workflows
   - Implement model training pipelines
   - Set up real-time prediction infrastructure

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss proposed modifications.

## Development Guidelines
- Use virtual environments for Python development
- Follow PEP 8 coding standards
- Document all functions and modules
- Maintain test coverage for new features
- Use Git for version control
- Keep sensitive data out of version control
- Ensure database and storage systems are clean and deduplicated

## License
This project is licensed under the MIT License. See the LICENSE file for details.


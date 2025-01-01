# Trading System Project

## Table of Contents

1. [Project Overview](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#project-overview)
2. [Current Status](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#current-status)
3. Features
   - [Database](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#database)
   - [Data Collection](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#data-collection)
   - [Storage Architecture](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#storage-architecture)
   - [Data Integrity](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#data-integrity)
   - [Docker Configuration](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#docker-configuration)
4. Setup Instructions
   - [Prerequisites](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#prerequisites)
   - [Installation Steps](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#installation-steps)
5. [Database Management](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#database-management)
6. [Data Verification](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#data-verification)
7. [Next Steps](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#next-steps)
8. [Contributing](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#contributing)
9. [Development Guidelines](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#development-guidelines)
10. [License](https://chatgpt.com/g/g-p-67600138979c8191990964ff66198ef5-etl-project/c/67755074-2b24-800f-b6f4-a2d011886e65#license)

------

## Project Overview

This Windows-based algorithmic trading system integrates TimescaleDB, Spark, and MetaTrader 5 to handle historical and real-time financial tick data. The system is designed for flexibility, scalability, and integration with analytics tools.

------

## Current Status

- ✓ Basic project structure established
- ✓ Spark cluster configured
- ✓ Docker environment tested
- ✓ Real-time and historical tick data collection implemented
- ✓ Hybrid storage system (Parquet and TimescaleDB) operational
- ✓ Deduplication and data integrity mechanisms in place

------

## Features

### Database

- Engine: TimescaleDB, optimized for time-series data
- Robust deduplication mechanisms
- Symbol Coverage: AUDUSD, BTCJPY, CHFJPY, EURUSD, GBPJPY, US30, USDJPY, USTEC, XAUUSD, BTCUSD

### Data Collection

1. Historical Data:
   - Script: `fetch_historical_data.py`
   - Fetches and deduplicates data from MetaTrader 5
   - Resumes from the last recorded tick
2. Real-Time Collection:
   - Script: `tick_collector.py`
   - Continuously collects live tick data
   - Saves to TimescaleDB and Parquet

### Storage Architecture

1. Parquet Files:

    Optimized for analytics workflows

   - Directory: `data/ticks/{SYMBOL}/{YYYYMMDD}.parquet`

2. **TimescaleDB:** Supports real-time querying and analytics

### Data Integrity

- Automatic deduplication
- Built-in data validation and verification tools

### Docker Configuration

- **TimescaleDB:** `docker-compose.timescaledb.yml`
- **Spark Environment:** `docker-compose.spark.yml`
- **Custom Configurations:** Included in `docker/config/`

------

## Setup Instructions

### Prerequisites

- Windows 11 with PowerShell 7+
- Docker Desktop
- Python 3.10+
- MetaTrader 5 terminal configured for your broker

### Installation Steps

1. **Clone Repository:**

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **Start Infrastructure:**

   ```bash
   docker-compose -f docker/docker-compose.timescaledb.yml up -d --build
   ```

3. **Initialize Database Schema:**

   ```bash
   docker cp docker/init-scripts/01-init-tables.sql market_data_db:/tmp/
   docker exec -it market_data_db psql -U market_collector -d market_data -f /tmp/01-init-tables.sql
   ```

4. **Start Data Collection:**

   - Historical Data:

     ```bash
     python scripts/fetch_historical_data.py
     ```

   - Real-Time Collection:

     ```bash
     python src/collectors/tick_collector.py
     ```

------

## Database Management

#### Connecting to TimescaleDB

```bash
docker exec -it market_data_db psql -U market_collector -d market_data
```

#### Example Queries

```sql
-- View data range by symbol
SELECT symbol, MIN(tick_time), MAX(tick_time)
FROM market_data.tick_data
GROUP BY symbol;

-- Check for duplicates
SELECT symbol, tick_time, COUNT(*)
FROM market_data.tick_data
GROUP BY symbol, tick_time
HAVING COUNT(*) > 1;
```

------

## Data Verification

**Script:** `verify_tick_data.py`

- Validates database and Parquet data integrity.
- Provides summaries and sample outputs.

------

## Next Steps

### AI/ML Trading Solution

- Feature Engineering:
  - Candlestick generation (1-minute, 5-minute intervals)
  - Calculate volatility, moving averages, etc.
- Model Training:
  - Develop predictive models for price movement
  - Train models on historical tick data
- Real-Time Predictions:
  - Deploy trained models for live market analysis

### Front-End Development

- Create a web-based dashboard:
  - Visualize live tick data
  - Display analytics (e.g., candlestick charts)
  - Integrate AI/ML predictions

------

## Contributing

Pull requests are welcome. For major changes, please open an issue to discuss proposed modifications.

------

## Development Guidelines

- Use virtual environments for Python development.
- Follow PEP 8 coding standards.
- Document all functions and modules.
- Maintain test coverage for new features.
- Use Git for version control.
- Exclude sensitive credentials from version control.

------

## License

This project is licensed under the MIT License. See the LICENSE file for details.
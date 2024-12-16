# Exness ETL

High-performance ETL pipeline for financial market data, integrating MetaTrader 5 with Apache Spark for scalable data processing. Specifically optimized for Exness broker data collection and processing.

## Features
- Real-time market data collection from MetaTrader 5
- Multi-timeframe data management (M1-MN1)
- Scalable data processing with Apache Spark
- Support for multiple trading instruments
- Background data collection service

## Supported Instruments
- XAUUSD (Gold)
- BTCUSD (Bitcoin)
- USTEC (US Tech 100)
- US500 (S&P 500)
- US30 (Dow Jones)
- AUDUSD (Australian Dollar)

## Requirements
- Windows 10/11
- Python 3.10
- MetaTrader 5
- Apache Spark

## Installation
1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Start data collection:
   ```bash
   .\start_collector.ps1
   ```
2. Process data with Spark:
   ```bash
   python spark_processor.py
   ```

## Project Structure
```
trading_system/
├── data/
│   ├── raw/          # Raw market data
│   └── processed/    # Processed data
├── background_collector.py
├── config.py
├── spark_processor.py
└── start_collector.ps1
```

## License
MIT

## Author
[Your Name]

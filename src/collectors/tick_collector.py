# tick_collector.py: Real-Time Tick Data Collector for MetaTrader 5

import threading
import logging
import MetaTrader5 as mt5
import psycopg2
import pandas as pd
from queue import Queue
from pathlib import Path
from datetime import datetime, time

# Configuration for PostgreSQL
POSTGRES_CONFIG = {
    "dbname": "market_data",
    "user": "market_collector",
    "password": "1331",
    "host": "localhost",
    "port": 15433,
}

# Directory for Parquet file storage
DATA_DIR = Path("C:/DevProjects/trading_system/data/ticks")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Symbols to collect data for
SYMBOLS = [
    "AUDUSD", "BTCJPY", "CHFJPY", "EURUSD",
    "GBPJPY", "US30", "USDJPY", "USTEC", "XAUUSD", "BTCUSD"
]

# Buffer for batch database writes
DATA_BUFFERS = {symbol: Queue() for symbol in SYMBOLS}

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def connect_to_postgres():
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to PostgreSQL: {e}")
        return None

def save_to_postgres(symbol):
    """Save data from the buffer to PostgreSQL in batches."""
    conn = connect_to_postgres()
    if not conn:
        return

    while True:
        data = []
        while not DATA_BUFFERS[symbol].empty():
            data.append(DATA_BUFFERS[symbol].get())

        if data:
            try:
                cursor = conn.cursor()
                query = """
                INSERT INTO market_data.tick_data (symbol, tick_time, bid_price, ask_price, spread)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                """
                cursor.executemany(query, data)
                conn.commit()
                logging.info(f"Saved {len(data)} ticks for {symbol} to PostgreSQL.")
            except Exception as e:
                logging.error(f"Error saving data to PostgreSQL for {symbol}: {e}")

        threading.Event().wait(15)  # Save every 15 seconds

    conn.close()

def save_to_parquet(symbol, tick):
    """Save tick data to Parquet file."""
    date = datetime.fromtimestamp(tick.time).strftime("%Y%m%d")
    file_path = DATA_DIR / symbol / f"{date}.parquet"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame([{  # Prepare DataFrame for saving
        "symbol": symbol,
        "tick_time": datetime.fromtimestamp(tick.time),
        "bid_price": tick.bid,
        "ask_price": tick.ask,
        "spread": tick.ask - tick.bid,
    }])

    try:
        if file_path.exists():
            existing = pd.read_parquet(file_path)
            df = pd.concat([existing, df]).drop_duplicates()
        df.to_parquet(file_path, index=False, engine="pyarrow", compression="snappy")
        logging.info(f"Saved tick data for {symbol} to {file_path}.")
    except Exception as e:
        logging.error(f"Error saving data to Parquet for {symbol}: {e}")

def is_market_open(symbol):
    """Check if the market is open for the given symbol."""
    now = datetime.now()

    # Forex symbols: Closed on weekends and 1 hour daily (e.g., 22:00-23:00 UTC)
    if symbol != "BTCUSD":
        if now.weekday() in (5, 6):  # Saturday or Sunday
            return False
        if time(22, 0) <= now.time() < time(23, 0):  # Daily maintenance hour
            return False

    # Additional check for MT5 server status
    if not mt5.symbol_info(symbol):
        logging.warning(f"Symbol {symbol} is not available or server is under maintenance.")
        return False

    return True

def collect_ticks(symbol):
    """Collect real-time ticks for a specific symbol."""
    while True:
        if not is_market_open(symbol):
            logging.info(f"Market is closed for {symbol}. Skipping tick collection.")
            threading.Event().wait(60)  # Wait for 1 minute before re-checking
            continue

        tick = mt5.symbol_info_tick(symbol)
        if tick:
            tick_data = (
                symbol,
                datetime.fromtimestamp(tick.time),
                tick.bid,
                tick.ask,
                tick.ask - tick.bid
            )
            DATA_BUFFERS[symbol].put(tick_data)
            save_to_parquet(symbol, tick)
        threading.Event().wait(0.1)  # Collect data every 100ms

def main():
    if not mt5.initialize():
        logging.error("MetaTrader 5 initialization failed.")
        return

    threads = []

    # Start PostgreSQL saving threads
    for symbol in SYMBOLS:
        t = threading.Thread(target=save_to_postgres, args=(symbol,), daemon=True)
        threads.append(t)
        t.start()

    # Start tick collection threads
    for symbol in SYMBOLS:
        t = threading.Thread(target=collect_ticks, args=(symbol,), daemon=True)
        threads.append(t)
        t.start()

    logging.info("Tick collector is running. Press Ctrl+C to stop.")
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        logging.info("Stopping tick collector...")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()

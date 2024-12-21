"""
fetch_historical_data.py

Purpose: Fetch historical tick data from MetaTrader 5 for configured symbols and store it in the database.
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import psycopg2
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Output to console
)

# Database connection settings
DB_CONFIG = {
    'dbname': 'market_data',
    'user': 'market_collector',
    'password': '1331',
    'host': 'localhost',
    'port': 15433
}

# Symbols to fetch data for
SYMBOLS = [
    'AUDUSD',
    'BTCJPY',
    'CHFJPY',
    'EURUSD',
    'GBPJPY',
    'US30',
    'USDJPY',
    'USTEC',
    'XAUUSD',
    'BTCUSD'
]

# Time range for fetching data
CHUNK_SIZE_SECONDS = 3600  # Fetch data in 1-hour chunks
START_DATE = datetime(2023, 1, 1)  # Fallback start date


def initialize_mt5():
    """Initialize the MetaTrader 5 connection."""
    if not mt5.initialize():
        logging.error(f"MetaTrader 5 initialization failed: {mt5.last_error()}")
        return False
    logging.info("MetaTrader 5 initialized successfully.")
    return True


def get_last_tick_time(symbol):
    """Retrieve the most recent tick time from the database for the given symbol."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(tick_time) FROM market_data.tick_data WHERE symbol = %s;
        """, (symbol,))
        last_tick_time = cursor.fetchone()[0]
        conn.close()
        logging.info(f"Last tick time for {symbol}: {last_tick_time}")
        return last_tick_time
    except Exception as e:
        logging.error(f"Error fetching last tick time for {symbol}: {e}")
        return None


def fetch_and_store_ticks(symbol, start_date, chunk_size_seconds):
    """Fetch historical tick data and store it in the database."""
    end_date = datetime.now()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        while start_date < end_date:
            chunk_end = start_date + timedelta(seconds=chunk_size_seconds)
            logging.info(f"Fetching ticks for {symbol} from {start_date} to {chunk_end}...")

            ticks = mt5.copy_ticks_range(symbol, start_date, chunk_end, mt5.COPY_TICKS_ALL)

            if ticks is None or len(ticks) == 0:
                logging.warning(f"No ticks retrieved for {symbol} from {start_date} to {chunk_end}.")
            else:
                df = pd.DataFrame(ticks)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                logging.info(f"Fetched {len(df)} ticks for {symbol}. Saving to database...")

                for _, row in df.iterrows():
                    cursor.execute("""
                        INSERT INTO market_data.tick_data (symbol, tick_time, bid_price, ask_price, last_price, volume, spread, tick_size)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (
                        symbol,
                        row['time'],
                        row['bid'],
                        row['ask'],
                        row.get('last', None),
                        row.get('volume', None),
                        row['ask'] - row['bid'],  # Calculate spread
                        None  # Tick size unavailable in MetaTrader 5 tick data
                    ))

                conn.commit()

            start_date = chunk_end

    except Exception as e:
        logging.error(f"Error fetching or storing data for {symbol}: {e}")
    finally:
        if conn:
            conn.close()


def main():
    """Main function to fetch historical tick data."""
    if not initialize_mt5():
        return

    for symbol in SYMBOLS:
        last_tick_time = get_last_tick_time(symbol)
        start_time = last_tick_time if last_tick_time else START_DATE
        fetch_and_store_ticks(symbol, start_time, CHUNK_SIZE_SECONDS)

    mt5.shutdown()
    logging.info("MetaTrader 5 shutdown.")


if __name__ == "__main__":
    main()

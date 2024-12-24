import logging
import MetaTrader5 as mt5
import psycopg2
from datetime import datetime, timedelta

# Symbols to fetch
SYMBOLS = [
    'AUDUSD', 'BTCJPY', 'CHFJPY', 'EURUSD',
    'GBPJPY', 'US30', 'USDJPY', 'USTEC', 'XAUUSD', 'BTCUSD'
]

# Database connection
DB_CONFIG = {
    'dbname': 'market_data',
    'user': 'market_collector',
    'password': '1331',
    'host': 'localhost',
    'port': '15433'
}

# Fetch last tick times from the database
def get_last_tick_times():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, MAX(tick_time) AS last_tick_time
        FROM market_data.tick_data
        GROUP BY symbol;
    """)
    result = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return result

# Fetch and store tick data
def fetch_and_store_ticks(symbol, start_time, end_time):
    logging.info(f"Fetching ticks for {symbol} from {start_time} to {end_time}...")
    ticks = mt5.copy_ticks_range(symbol, start_time, end_time, mt5.COPY_TICKS_ALL)

    if ticks is None or len(ticks) == 0:
        logging.warning(f"No ticks retrieved for {symbol} from {start_time} to {end_time}.")
        return

    logging.info(f"Fetched {len(ticks)} ticks for {symbol}. Saving to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for tick in ticks:
        try:
            cursor.execute("""
                INSERT INTO market_data.tick_data (symbol, tick_time, bid_price, ask_price, last_price, volume, spread, tick_size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, tick_time, bid_price, ask_price) DO NOTHING;
            """, (
                symbol,
                datetime.fromtimestamp(float(tick['time'])),  # Convert to timestamp
                float(tick['bid']),  # Convert bid price to float
                float(tick['ask']),  # Convert ask price to float
                float(tick['last']) if 'last' in tick.dtype.names else None,  # Last price if available
                int(tick['volume']) if 'volume' in tick.dtype.names else None,  # Volume if available
                float(tick['ask'] - tick['bid']),  # Calculate spread
                float(tick['volume_real']) if 'volume_real' in tick.dtype.names else None  # Real volume if available
            ))
        except Exception as e:
            logging.error(f"Error inserting tick for {symbol}: {e}")

    conn.commit()
    conn.close()

# Main function
def main():
    if not mt5.initialize():
        logging.error("MetaTrader 5 initialization failed.")
        return

    logging.info(f"Connected to terminal at: {mt5.terminal_info().path}")

    last_tick_times = get_last_tick_times()
    now = datetime.now()
    lookback_hours = 3  # Query 3 hours back if the last tick time is too old or missing

    for symbol in SYMBOLS:
        start_time = last_tick_times.get(symbol, now - timedelta(hours=lookback_hours))
        end_time = now

        while start_time < end_time:
            chunk_end_time = start_time + timedelta(hours=1)
            if chunk_end_time > end_time:
                chunk_end_time = end_time

            fetch_and_store_ticks(symbol, start_time, chunk_end_time)
            start_time = chunk_end_time

    mt5.shutdown()
    logging.info("MetaTrader 5 connection closed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

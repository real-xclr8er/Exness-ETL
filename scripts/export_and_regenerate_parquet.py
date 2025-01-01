import psycopg2
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Database connection settings
DB_CONFIG = {
    "dbname": "market_data",
    "user": "market_collector",
    "password": "1331",
    "host": "localhost",
    "port": 15433,
}

# Parquet output directory
OUTPUT_DIR = Path("C:/DevProjects/trading_system/data/ticks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

# Function to fetch symbols
def fetch_symbols(conn):
    query = "SELECT DISTINCT symbol FROM tick_data;"
    symbols = pd.read_sql_query(query, conn)["symbol"].tolist()
    print(f"Symbols found: {symbols}")
    return symbols

# Function to get the minimum available tick time for a symbol
def get_min_tick_time(conn, symbol):
    query = """
        SELECT MIN(tick_time) as min_time
        FROM tick_data
        WHERE symbol = %s;
    """
    try:
        result = pd.read_sql_query(query, conn, params=(symbol,))
        return result["min_time"].iloc[0] if not result.empty else None
    except Exception as e:
        print(f"Error fetching minimum tick time for {symbol} from database: {e}")
        return None

# Function to fetch tick data in chunks
def fetch_tick_data_chunked(conn, symbol, start_time, chunk_days=30):
    chunk_end_time = start_time + timedelta(days=chunk_days)
    query = """
        SELECT tick_time, bid_price, ask_price, last_price, volume
        FROM tick_data
        WHERE symbol = %s AND tick_time >= %s AND tick_time < %s
        ORDER BY tick_time;
    """
    try:
        params = (symbol, start_time, chunk_end_time)
        df = pd.read_sql_query(query, conn, params=params)
        if not df.empty:
            df['spread'] = df['ask_price'] - df['bid_price']
            df['tick_size'] = None  # Placeholder
        return df, chunk_end_time
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame(), chunk_end_time

# Function to save to Parquet
def save_to_parquet(df, symbol):
    if df.empty:
        print(f"No data found for {symbol}. Skipping.")
        return

    df['date'] = pd.to_datetime(df['tick_time']).dt.strftime('%Y%m%d')
    for date, group in df.groupby('date'):
        output_path = OUTPUT_DIR / symbol / f"{date}.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            try:
                existing_data = pd.read_parquet(output_path)
                group = pd.concat([existing_data, group]).drop_duplicates(
                    subset=["tick_time", "bid_price", "ask_price"]
                )
            except Exception as e:
                print(f"Error reading existing file {output_path}: {e}")

        group.drop(columns='date', inplace=True)
        group.to_parquet(output_path, index=False, engine="pyarrow", compression="snappy")
        print(f"Saved {len(group)} rows to {output_path}")

# Main function
def main():
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)

        symbols = fetch_symbols(conn)
        print(f"Fetched symbols: {symbols}")

        for symbol in symbols:
            print(f"Processing symbol: {symbol}")

            min_time_db = get_min_tick_time(conn, symbol)

            start_time = min_time_db
            if not start_time:
                print(f"No data found for {symbol}. Skipping.")
                continue

            print(f"Starting from: {start_time} for {symbol}")

            while start_time < datetime.now():
                tick_data, next_start_time = fetch_tick_data_chunked(conn, symbol, start_time)
                print(f"Fetched {len(tick_data)} rows for {symbol} from {start_time} to {next_start_time}")

                save_to_parquet(tick_data, symbol)
                start_time = next_start_time

        print("Parquet export and regeneration complete.")

    except Exception as e:
        print(f"Error during export: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    main()

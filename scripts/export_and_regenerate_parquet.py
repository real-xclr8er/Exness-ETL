"""
export_and_regenerate_parquet_debug.py

Purpose:
Debugging the Parquet export script by incrementally enabling sections.
Enhanced to start data collection from the last processed timestamp in database or Parquet.
"""

import psycopg2
import pandas as pd
from pathlib import Path
from datetime import datetime

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

# Function to fetch symbols
def fetch_symbols(conn):
    """
    Fetch all unique symbols from the database.
    """
    query = "SELECT DISTINCT symbol FROM tick_data;"
    symbols = pd.read_sql_query(query, conn)["symbol"].tolist()
    print(f"Symbols found: {symbols}")
    return symbols

# Function to get the last processed timestamp from the database
def get_last_processed_time_db(conn, symbol):
    """
    Retrieve the latest tick_time for a symbol from the database.
    """
    query = """
        SELECT MAX(tick_time) as last_time
        FROM tick_data
        WHERE symbol = %s;
    """
    try:
        result = pd.read_sql_query(query, conn, params=(symbol,))
        return result["last_time"].iloc[0] if not result.empty else None
    except Exception as e:
        print(f"Error fetching last processed time for {symbol} from database: {e}")
        return None

# Function to get the last processed timestamp from Parquet files
def get_last_processed_time_parquet(symbol):
    """
    Retrieve the latest tick_time for a symbol from existing Parquet files.
    """
    parquet_dir = OUTPUT_DIR / symbol
    try:
        if not parquet_dir.exists():
            return None

        latest_file = max(parquet_dir.glob("*.parquet"), key=lambda f: f.name, default=None)
        if latest_file:
            df = pd.read_parquet(latest_file)
            return df["tick_time"].max()
    except Exception as e:
        print(f"Error fetching last processed time for {symbol} from Parquet: {e}")
    return None

# Function to fetch tick data starting from the last processed time
def fetch_tick_data(conn, symbol, start_time):
    """
    Fetch tick data for a specific symbol from the database starting from the last processed time.
    """
    query = """
        SELECT tick_time, bid_price, ask_price, last_price, volume
        FROM tick_data
        WHERE symbol = %s AND tick_time > %s
        ORDER BY tick_time;
    """
    try:
        df = pd.read_sql_query(query, conn, params=(symbol, start_time))
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# Function to save to Parquet
def save_to_parquet(df, symbol):
    """
    Save the DataFrame to Parquet files organized by date.
    Handles deduplication and merging with existing files.
    """
    if df.empty:
        print(f"No data found for {symbol}. Skipping.")
        return

    df['date'] = pd.to_datetime(df['tick_time']).dt.strftime('%Y%m%d')  # Extract date
    for date, group in df.groupby('date'):
        date_str = date
        output_path = OUTPUT_DIR / symbol / f"{date_str}.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle merging with existing files
        if output_path.exists():
            try:
                existing_data = pd.read_parquet(output_path)
                group = pd.concat([existing_data, group]).drop_duplicates(
                    subset=["tick_time", "bid_price", "ask_price"]
                )
            except Exception as e:
                print(f"Error reading existing file {output_path}: {e}")

        # Save to Parquet
        group.drop(columns='date', inplace=True)
        group.to_parquet(output_path, index=False, engine="pyarrow", compression="snappy")
        print(f"Saved {len(group)} rows to {output_path}")

# Main function
def main():
    """
    Main function to export and regenerate Parquet files for all symbols.
    Incremental debugging enabled.
    """
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)

        # Fetch symbols
        symbols = fetch_symbols(conn)
        print(f"Fetched symbols: {symbols}")

        # Process each symbol
        for symbol in symbols:
            print(f"Processing symbol: {symbol}")

            # Get last processed time from both database and Parquet
            last_time_db = get_last_processed_time_db(conn, symbol)
            last_time_parquet = get_last_processed_time_parquet(symbol)

            # Determine the most recent timestamp
            start_time = max(last_time_db, last_time_parquet) if last_time_db and last_time_parquet else last_time_db or last_time_parquet
            print(f"Starting from: {start_time} for {symbol}")

            # Fetch new tick data
            tick_data = fetch_tick_data(conn, symbol, start_time)
            print(tick_data.head())  # Display a preview of the data

            # Save to Parquet
            save_to_parquet(tick_data, symbol)

        print("Parquet export and regeneration complete.")

    except Exception as e:
        print(f"Error during export: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    main()

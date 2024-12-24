"""
export_and_regenerate_parquet.py

Purpose:
Combines the functionality of exporting and regenerating Parquet files from TimescaleDB.
Features include dynamic symbol detection, deduplication, and file merging.
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
OUTPUT_DIR = Path("data/ticks")

def fetch_symbols(conn):
    """
    Fetch all unique symbols from the database.
    """
    query = "SELECT DISTINCT symbol FROM tick_data;"
    symbols = pd.read_sql_query(query, conn)["symbol"].tolist()
    print(f"Symbols found: {symbols}")
    return symbols

def fetch_tick_data(conn, symbol):
    """
    Fetch all tick data for a specific symbol from the database.
    """
    query = """
        SELECT tick_time, bid_price, ask_price, last_price, volume
        FROM tick_data
        WHERE symbol = %s
        ORDER BY tick_time;
    """
    try:
        df = pd.read_sql_query(query, conn, params=(symbol,))
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

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

def main():
    """
    Main function to export and regenerate Parquet files for all symbols.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        symbols = fetch_symbols(conn)

        for symbol in symbols:
            print(f"Processing symbol: {symbol}")
            tick_data = fetch_tick_data(conn, symbol)
            save_to_parquet(tick_data, symbol)

        print("Parquet export and regeneration complete.")
    except Exception as e:
        print(f"Error during export: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()

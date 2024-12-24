#!/usr/bin/env python3
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import logging
from pathlib import Path
import threading
import queue
import psycopg2

class TickCollector:
    def __init__(self, config_path="configs/collector_config.yml"):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        # Load configuration
        self.symbols = ["AUDUSD", "BTCUSD", "US30", "US500", "USTEC", "XAUUSD"]
        self.storage_path = Path("data/ticks")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.db_config = {
            "dbname": "market_data",
            "user": "market_collector",
            "password": "1331",
            "host": "localhost",
            "port": 15433
        }

        self.running = threading.Event()
        self.threads = {}
        self.data_queues = {symbol: queue.Queue() for symbol in self.symbols}

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("tick_collector.log"), logging.StreamHandler()]
        )
        self.logger.info("Logging initialized.")

    def initialize_mt5(self):
        if not mt5.initialize():
            self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False
        self.logger.info("MT5 initialized successfully.")
        return True

    def collect_symbol_ticks(self, symbol):
        self.logger.info(f"Starting tick collection for {symbol}")
        while self.running.is_set():
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                tick_data = {
                    'time': datetime.fromtimestamp(tick.time_msc / 1000.0, tz=timezone.utc),
                    'bid': tick.bid,
                    'ask': tick.ask,
                    'last': getattr(tick, 'last', None),
                    'volume': getattr(tick, 'volume', None)
                }
                self.data_queues[symbol].put(tick_data)
            threading.Event().wait(0.01)

    def save_ticks(self, symbol, ticks):
        # Save to Parquet
        file_path = self.storage_path / f"{symbol}/{datetime.now().strftime('%Y%m%d')}.parquet"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if file_path.exists():
                existing_data = pd.read_parquet(file_path)
                new_data = pd.DataFrame(ticks)
                combined_data = pd.concat([existing_data, new_data]).drop_duplicates()
            else:
                combined_data = pd.DataFrame(ticks)
            combined_data.to_parquet(file_path, engine="pyarrow", index=False, compression="snappy")
            self.logger.info(f"Saved {len(ticks)} ticks for {symbol} to Parquet.")
        except Exception as e:
            self.logger.error(f"Error saving ticks for {symbol} to Parquet: {e}")

        # Save to TimescaleDB
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            for tick in ticks:
                cursor.execute(
                    """
                    INSERT INTO tick_data (symbol, tick_time, bid_price, ask_price, last_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (symbol, tick['time'], tick['bid'], tick['ask'], tick.get('last'), tick.get('volume'))
                )
            conn.commit()
            cursor.close()
            conn.close()
            self.logger.info(f"Saved {len(ticks)} ticks for {symbol} to TimescaleDB.")
        except Exception as e:
            self.logger.error(f"Error saving ticks for {symbol} to TimescaleDB: {e}")

    def process_queues(self):
        while self.running.is_set():
            for symbol, q in self.data_queues.items():
                if not q.empty():
                    ticks = []
                    while not q.empty():
                        ticks.append(q.get())
                    self.save_ticks(symbol, ticks)
            threading.Event().wait(1)

    def start(self):
        if not self.initialize_mt5():
            return
        self.running.set()
        for symbol in self.symbols:
            thread = threading.Thread(target=self.collect_symbol_ticks, args=(symbol,))
            thread.start()
            self.threads[symbol] = thread
        threading.Thread(target=self.process_queues).start()
        self.logger.info("Tick collection started.")

    def stop(self):
        self.running.clear()
        for thread in self.threads.values():
            thread.join()
        mt5.shutdown()
        self.logger.info("Tick collection stopped.")

if __name__ == "__main__":
    collector = TickCollector()
    try:
        collector.start()
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        collector.stop()

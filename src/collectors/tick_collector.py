"""
src/collectors/tick_collector.py

Real-time tick data collector for MetaTrader 5 with system tray interface
======================================================================
Collects and stores tick data with system tray monitoring and control.
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
import threading
import queue
import time
import yaml
from typing import Dict
import psycopg2


class TickCollector:
    def __init__(self, config_path: str = "configs/collector_config.yml"):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()  # Set up logging system

        # Load configuration
        self.config = self.load_config(config_path)
        self.symbols = self.config.get("symbols", ["AUDUSD", "BTCUSD", "US30", "US500", "USTEC", "XAUUSD"])

        # Initialize storage paths
        self.storage_path = Path(self.config.get('storage_path', 'data/ticks'))
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Data collection settings
        self.batch_size = self.config.get('batch_size', 1000)
        self.save_interval = self.config.get('save_interval', 300)

        # Database connection
        self.db_config = self.config.get("db_config", {
            "dbname": "market_data",
            "user": "market_collector",
            "password": "1331",
            "host": "localhost",
            "port": 15433
        })

        # Threading and data storage
        self.running = threading.Event()
        self.threads: Dict[str, threading.Thread] = {}
        self.data_queues: Dict[str, queue.Queue] = {}
        self.tick_counts: Dict[str, int] = {symbol: 0 for symbol in self.symbols}
        self.last_save_time = datetime.now()
        self.status = "Stopped"

    def setup_logging(self):
        """Set up logging for the application."""
        log_file = "tick_collector.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),  # Log to file
                logging.StreamHandler()         # Log to console
            ]
        )
        self.logger.info("Logging system initialized successfully.")

    def load_config(self, config_path: str):
        """Load configuration from a YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.warning(f"Configuration file not found: {config_path}. Using defaults.")
            return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Error reading configuration file: {e}")
            return {}

    def initialize_mt5(self):
        """Initialize connection to MetaTrader 5."""
        if not mt5.initialize():
            self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False
        self.logger.info("MT5 initialized successfully.")
        return True

    def collect_symbol_ticks(self, symbol: str, data_queue: queue.Queue):
        """Collect tick data for a given symbol."""
        self.logger.info(f"Starting tick collection for {symbol}")
        while self.running.is_set():
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                data_queue.put({
                    'time': datetime.fromtimestamp(tick.time_msc / 1000.0),
                    'bid': tick.bid,
                    'ask': tick.ask,
                    'last': tick.last,
                    'volume': tick.volume
                })
                self.tick_counts[symbol] += 1
            time.sleep(0.01)  # Avoid overloading the system
        self.logger.info(f"Stopped collecting ticks for {symbol}")

    def process_queue(self):
        """Process data queues and save tick data to files and TimescaleDB periodically."""
        while self.running.is_set():
            now = datetime.now()
            if (now - self.last_save_time).seconds >= self.save_interval:
                for symbol, data_queue in self.data_queues.items():
                    if not data_queue.empty():
                        ticks = []
                        while not data_queue.empty():
                            ticks.append(data_queue.get())
                        if ticks:
                            self.save_ticks(symbol, ticks)
                self.last_save_time = now
            time.sleep(1)

    def save_ticks(self, symbol: str, ticks: list):
        """Save collected tick data to Parquet files and TimescaleDB."""
        # Save to Parquet file
        file_path = self.storage_path / f"{symbol}/{datetime.now().strftime('%Y%m%d')}.parquet"
        try:
            if file_path.exists():
                existing_data = pd.read_parquet(file_path)
                new_data = pd.DataFrame(ticks)
                combined_data = pd.concat([existing_data, new_data], ignore_index=True)
            else:
                combined_data = pd.DataFrame(ticks)

            # Save updated data
            file_path.parent.mkdir(parents=True, exist_ok=True)
            combined_data.to_parquet(file_path, engine="pyarrow", index=False, compression='snappy')
            self.logger.info(f"Saved {len(ticks)} ticks for {symbol} to {file_path}")

        except Exception as e:
            self.logger.error(f"Error saving ticks for {symbol} to Parquet: {e}")

        # Save to TimescaleDB
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            for tick in ticks:
                cursor.execute("""
                    INSERT INTO tick_data (symbol, tick_time, bid_price, ask_price, last_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    symbol,
                    tick['time'],
                    tick['bid'],
                    tick['ask'],
                    tick.get('last', None),
                    tick.get('volume', None)
                ))
            conn.commit()
            cursor.close()
            conn.close()
            self.logger.info(f"Saved {len(ticks)} ticks for {symbol} to TimescaleDB.")
        except Exception as e:
            self.logger.error(f"Error saving ticks for {symbol} to TimescaleDB: {e}")

    def start_collection(self):
        """Start the tick collection process."""
        if not self.initialize_mt5():
            return
        self.running.set()
        self.status = "Running"
        self.data_queues = {symbol: queue.Queue() for symbol in self.symbols}
        self.logger.info("Tick collection started.")

        # Start threads for each symbol
        for symbol in self.symbols:
            thread = threading.Thread(target=self.collect_symbol_ticks, args=(symbol, self.data_queues[symbol]))
            thread.start()
            self.threads[symbol] = thread

        # Start the queue processing thread
        self.process_thread = threading.Thread(target=self.process_queue)
        self.process_thread.start()

    def stop_collection(self):
        """Stop the tick collection process."""
        self.logger.info("Stopping tick collection...")
        self.running.clear()
        for thread in self.threads.values():
            thread.join()
        self.process_thread.join()
        mt5.shutdown()
        self.logger.info("Tick collection stopped.")

    def run(self):
        """Run the collector."""
        try:
            self.start_collection()
            while self.running.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt detected. Stopping...")
            self.stop_collection()


def main():
    """Main function to run the collector."""
    collector = TickCollector()
    collector.run()


if __name__ == "__main__":
    main()

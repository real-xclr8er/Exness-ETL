# background_collector.py

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from pathlib import Path
import sys
import signal
from config import SYMBOLS, Timeframe, DATA_FOLDER

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(DATA_FOLDER) / "collector.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.is_running = True
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
    def handle_signal(self, signum, frame):
        logger.info("Received stop signal. Shutting down...")
        self.is_running = False
        
    def initialize_mt5(self):
        """Initialize MT5 connection"""
        if not mt5.initialize():
            raise ConnectionError(f"MT5 initialization failed: {mt5.last_error()}")
        logger.info("MT5 initialized successfully")
        
    def save_data(self, df, symbol, timeframe):
        """Save data with timestamp-based partitioning"""
        if df is None or df.empty:
            return
            
        try:
            folder = Path(DATA_FOLDER) / symbol / timeframe.name
            folder.mkdir(parents=True, exist_ok=True)
            
            current_date = datetime.now().strftime('%Y%m%d')
            filename = f"{symbol}_{timeframe.name}_{current_date}.csv"
            filepath = folder / filename
            
            # Append data or create new file
            df.to_csv(filepath, mode='a', header=not filepath.exists(), index=False)
            logger.info(f"Saved {len(df)} records for {symbol} {timeframe.name}")
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            
    def collect_data(self):
        """Collect data for all symbols and timeframes"""
        try:
            for symbol in SYMBOLS:
                for timeframe in Timeframe:
                    logger.info(f"Collecting data for {symbol} {timeframe.name}")
                    try:
                        # Get new data
                        rates = mt5.copy_rates_from(symbol, timeframe.value, 
                                                  datetime.now(), 1000)
                        if rates is not None:
                            df = pd.DataFrame(rates)
                            df['time'] = pd.to_datetime(df['time'], unit='s')
                            self.save_data(df, symbol, timeframe)
                        else:
                            logger.warning(f"No data received for {symbol} {timeframe.name}")
                            
                    except Exception as e:
                        logger.error(f"Error collecting {symbol} {timeframe.name}: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Collection error: {str(e)}")
            
    def run(self):
        """Main collection loop"""
        try:
            self.initialize_mt5()
            
            while self.is_running:
                try:
                    self.collect_data()
                    time.sleep(60)  # Wait 1 minute between collections
                    
                except Exception as e:
                    logger.error(f"Main loop error: {str(e)}")
                    time.sleep(60)  # Wait before retry
                    
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            
        finally:
            mt5.shutdown()
            logger.info("Collector stopped")

if __name__ == "__main__":
    # Create data folder if it doesn't exist
    Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)
    
    collector = DataCollector()
    collector.run()
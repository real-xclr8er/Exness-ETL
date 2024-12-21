"""
verify_tick_data_with_terminal_info.py

Purpose: Verify if historical tick data is available for a specific symbol over the last 2 days.
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Output to console
)

# Initialize MetaTrader 5 connection
if not mt5.initialize():
    logging.error(f"Failed to initialize MT5: {mt5.last_error()}")
    exit()

# Display terminal information
terminal_info = mt5.terminal_info()
if terminal_info is not None:
    logging.info(f"Connected to terminal at: {terminal_info.path}")
else:
    logging.warning("Failed to retrieve terminal information.")

# Symbol and time range to test
symbol = "BTCUSD"  # Replace with your desired symbol
end_time = datetime.now()
start_time = end_time - timedelta(days=2)  # Last 2 days

logging.info(f"Checking tick data for {symbol} from {start_time} to {end_time}...")

# Fetch tick data
ticks = mt5.copy_ticks_range(symbol, start_time, end_time, mt5.COPY_TICKS_ALL)

# Check and display results
if ticks is None or len(ticks) == 0:
    logging.warning(f"No tick data available for {symbol} in the specified range.")
else:
    logging.info(f"Retrieved {len(ticks)} ticks for {symbol} in the specified range.")
    logging.info("Sample data from the retrieved ticks:")
    # Print first few rows if data is available
    for tick in ticks[:5]:  # Print a maximum of 5 rows for demonstration
        logging.info(tick)

# Shutdown MetaTrader 5 connection
mt5.shutdown()
logging.info("MetaTrader 5 connection closed.")

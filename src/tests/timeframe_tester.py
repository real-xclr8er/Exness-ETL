"""
src/utils/timeframe_tester.py

Comprehensive Timeframe Tester
============================

This script tests the availability of all standard timeframes in MetaTrader 5,
from very short intervals up to monthly timeframes. It also includes functionality
to sample tick data for more granular analysis.
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import logging
from pathlib import Path
import time


class TimeframeTester:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        # Our specific symbols to test
        self.symbols = [
            "AUDUSD", "BTCUSD", "US30", "US500",
            "USTEC", "XAUUSD"
        ]

        # Complete dictionary of all standard timeframes
        self.timeframes = {
            # Minutes
            'M1': mt5.TIMEFRAME_M1,
            'M2': mt5.TIMEFRAME_M2,
            'M3': mt5.TIMEFRAME_M3,
            'M4': mt5.TIMEFRAME_M4,
            'M5': mt5.TIMEFRAME_M5,
            'M6': mt5.TIMEFRAME_M6,
            'M10': mt5.TIMEFRAME_M10,
            'M12': mt5.TIMEFRAME_M12,
            'M15': mt5.TIMEFRAME_M15,
            'M20': mt5.TIMEFRAME_M20,
            'M30': mt5.TIMEFRAME_M30,

            # Hours
            'H1': mt5.TIMEFRAME_H1,
            'H2': mt5.TIMEFRAME_H2,
            'H3': mt5.TIMEFRAME_H3,
            'H4': mt5.TIMEFRAME_H4,
            'H6': mt5.TIMEFRAME_H6,
            'H8': mt5.TIMEFRAME_H8,
            'H12': mt5.TIMEFRAME_H12,

            # Days and above
            'D1': mt5.TIMEFRAME_D1,
            'W1': mt5.TIMEFRAME_W1,
            'MN1': mt5.TIMEFRAME_MN1
        }

    def setup_logging(self):
        """Configure logging with both file and console output"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('timeframe_test.log'),
                logging.StreamHandler()
            ]
        )

    def initialize_mt5(self):
        """Initialize connection to MetaTrader 5"""
        if not mt5.initialize():
            self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False
        return True

    def test_tick_data(self, symbol: str, duration_seconds: int = 10):
        """
        Test tick data availability and frequency for a symbol
        
        Args:
            symbol: Trading symbol to test
            duration_seconds: How long to collect tick data
        """
        try:
            self.logger.info(f"Testing tick data for {symbol} over {duration_seconds} seconds")
            
            # Get current time
            start_time = datetime.now()
            ticks = []
            
            # Collect ticks for the specified duration
            while (datetime.now() - start_time).seconds < duration_seconds:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    ticks.append({
                        'time': datetime.fromtimestamp(tick.time_msc / 1000.0),
                        'bid': tick.bid,
                        'ask': tick.ask,
                        'last': tick.last,
                        'volume': tick.volume
                    })
                time.sleep(0.001)  # Tiny sleep to prevent overwhelming the system
            
            # Analyze tick frequency
            if ticks:
                df_ticks = pd.DataFrame(ticks)
                tick_count = len(df_ticks)
                unique_times = len(df_ticks['time'].unique())
                avg_ticks_per_second = tick_count / duration_seconds
                
                return {
                    'total_ticks': tick_count,
                    'unique_timestamps': unique_times,
                    'ticks_per_second': avg_ticks_per_second,
                    'sample_data': df_ticks.head()
                }
            return {'error': 'No ticks collected'}
            
        except Exception as e:
            return {'error': str(e)}

    def test_timeframe_availability(self, symbol: str, timeframe: int):
        """
        Test data availability for a specific symbol and timeframe
        """
        try:
            # Get current time
            end_time = datetime.now()
            # Try to get last hour of data
            start_time = end_time - timedelta(hours=1)
            
            # Time the data request
            start_request = datetime.now()
            rates = mt5.copy_rates_range(
                symbol,
                timeframe,
                start_time,
                end_time
            )
            request_time = (datetime.now() - start_request).total_seconds()
            
            if rates is not None and len(rates) > 0:
                return {
                    'available': True,
                    'count': len(rates),
                    'request_time': request_time,
                    'first_time': pd.to_datetime(rates[0]['time'], unit='s'),
                    'last_time': pd.to_datetime(rates[-1]['time'], unit='s')
                }
            else:
                return {
                    'available': False,
                    'error': 'No data returned'
                }

        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }

    def run_complete_test(self):
        """
        Run both timeframe and tick data tests for all symbols
        """
        if not self.initialize_mt5():
            return None
            
        results = []
        tick_results = []
        
        # Test standard timeframes
        for symbol in self.symbols:
            self.logger.info(f"\nTesting symbol: {symbol}")
            
            # Test tick data first
            tick_data = self.test_tick_data(symbol)
            tick_results.append({
                'symbol': symbol,
                **tick_data
            })
            
            # Then test each timeframe
            for timeframe_name, timeframe_value in self.timeframes.items():
                self.logger.info(f"  Testing timeframe: {timeframe_name}")
                test_result = self.test_timeframe_availability(symbol, timeframe_value)
                test_result['symbol'] = symbol
                test_result['timeframe'] = timeframe_name
                results.append(test_result)
        
        # Convert results to DataFrames
        df_results = pd.DataFrame(results)
        df_tick_results = pd.DataFrame(tick_results)
        
        # Save results
        df_results.to_csv('timeframe_test_results.csv', index=False)
        df_tick_results.to_csv('tick_test_results.csv', index=False)
        
        mt5.shutdown()
        return df_results, df_tick_results

def main():
    """
    Run the complete test suite and display results
    """
    tester = TimeframeTester()
    timeframe_results, tick_results = tester.run_complete_test()
    
    if timeframe_results is not None:
        print("\nTimeframe Test Results Summary:")
        print("==============================")
        summary = timeframe_results.groupby(['symbol', 'timeframe'])['available'].first()
        print(summary.to_string())
        
        print("\nTick Data Summary:")
        print("=================")
        print(tick_results[['symbol', 'total_ticks', 'ticks_per_second']].to_string())
        
        print("\nDetailed results have been saved to CSV files")

if __name__ == "__main__":
    main()

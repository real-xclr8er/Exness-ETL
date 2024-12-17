"""
src/processors/price_processor.py

Basic Price Data Processor
=========================

This module handles the processing of 15-second market data into larger timeframes
while managing common edge cases in financial data processing.

Key Features:
- Reads 15-second price data from Parquet files
- Aggregates data into larger timeframes (1min, 5min, etc.)
- Handles common edge cases like market gaps and data issues
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

class PriceProcessor:
    def __init__(self, data_path: str):
        # Set up logging for tracking processing operations
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Path where our 15-second data is stored
        self.data_path = Path(data_path)
        
        # Dictionary to store our processing rules for edge cases
        self.edge_case_handlers = {
            'missing_data': self._handle_missing_data,
            'market_gap': self._handle_market_gap,
            'news_event': self._handle_news_event
        }

    def read_raw_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Reads 15-second data for a given symbol and date range.
        
        Args:
            symbol: The trading symbol (e.g., 'BTCUSD')
            start_date: Start of the data range
            end_date: End of the data range
            
        Returns:
            DataFrame containing the raw price data
        """
        try:
            # Create a list of dates we need to read
            date_range = pd.date_range(start_date, end_date, freq='D')
            data_frames = []

            for date in date_range:
                file_path = self.data_path / symbol / f"{date.strftime('%Y%m%d')}.parquet"
                
                if file_path.exists():
                    # Read the parquet file for this date
                    df = pd.read_parquet(file_path)
                    data_frames.append(df)
                else:
                    self.logger.warning(f"No data file found for {symbol} on {date}")

            if not data_frames:
                raise ValueError(f"No data found for {symbol} between {start_date} and {end_date}")

            # Combine all the daily data
            combined_data = pd.concat(data_frames)
            
            # Sort by time and remove any duplicates
            combined_data = combined_data.sort_index().loc[start_date:end_date]
            return combined_data.loc[~combined_data.index.duplicated(keep='last')]

        except Exception as e:
            self.logger.error(f"Error reading data for {symbol}: {str(e)}")
            raise

    def aggregate_timeframe(self, data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """
        Aggregates 15-second data into larger timeframes.
        
        Args:
            data: DataFrame containing 15-second data
            timeframe: Target timeframe (e.g., '1min', '5min', '1H')
            
        Returns:
            DataFrame with aggregated data
        """
        try:
            # Define our aggregation rules
            agg_rules = {
                'bid': 'last',    # Last bid price in the period
                'ask': 'last',    # Last ask price in the period
                'volume': 'sum'   # Sum of volume in the period
            }

            # Resample to the target timeframe
            resampled = data.resample(timeframe).agg(agg_rules)

            # Now let's handle edge cases in our resampled data
            resampled = self._process_edge_cases(resampled)

            return resampled

        except Exception as e:
            self.logger.error(f"Error aggregating timeframe {timeframe}: {str(e)}")
            raise

    def _process_edge_cases(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Processes common edge cases in the data.
        
        Args:
            data: DataFrame containing price data
            
        Returns:
            DataFrame with edge cases handled
        """
        # Check for missing data (gaps in our time series)
        data = self._handle_missing_data(data)
        
        # Check for market gaps (weekends, holidays)
        data = self._handle_market_gap(data)
        
        # Handle any known news events
        data = self._handle_news_event(data)
        
        return data

    def _handle_missing_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Handles missing data points in our time series.
        Missing data might occur due to network issues or other technical problems.
        """
        # Find gaps in our time series
        time_diff = data.index.to_series().diff()
        
        # Log any gaps we find
        gaps = time_diff[time_diff > pd.Timedelta('30s')]
        for time, gap in gaps.items():
            self.logger.warning(f"Data gap detected at {time}, duration: {gap}")
        
        # For small gaps (< 1 minute), we'll forward fill the last known price
        return data.ffill(limit=4)  # limit=4 means we'll only fill up to 1 minute

    def _handle_market_gap(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Handles market gaps like weekends and holidays.
        These are expected gaps where we don't want to fill in data.
        """
        for idx in data.index:
            # Check if it's a weekend (except for BTCUSD)
            if idx.weekday() >= 5 and 'BTCUSD' not in str(data.name):
                # Mark weekend data as NaN
                data.loc[idx] = None
                
        return data

    def _handle_news_event(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Marks periods with significant news events.
        This helps identify potentially volatile periods.
        """
        # In a real system, we'd load news events from a calendar
        # For now, we'll just add a placeholder column
        data['news_event'] = False
        
        # Here you could add logic to mark known news events
        # Example: FOMC meetings, NFP releases, etc.
        
        return data

    def process_symbol(self, symbol: str, start_date: datetime, end_date: datetime, 
                      timeframe: str) -> pd.DataFrame:
        """
        Complete processing pipeline for a symbol.
        
        Args:
            symbol: Trading symbol to process
            start_date: Start of the data range
            end_date: End of the data range
            timeframe: Target timeframe for aggregation
            
        Returns:
            Processed and aggregated DataFrame
        """
        # Read the raw data
        raw_data = self.read_raw_data(symbol, start_date, end_date)
        
        # Aggregate to desired timeframe
        processed_data = self.aggregate_timeframe(raw_data, timeframe)
        
        return processed_data
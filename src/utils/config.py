# config.py

from enum import Enum
import MetaTrader5 as mt5

class Timeframe(Enum):
    """Timeframe mappings to MT5 constants"""
    M1 = mt5.TIMEFRAME_M1
    M2 = mt5.TIMEFRAME_M2
    M3 = mt5.TIMEFRAME_M3
    M4 = mt5.TIMEFRAME_M4
    M5 = mt5.TIMEFRAME_M5
    M6 = mt5.TIMEFRAME_M6
    M10 = mt5.TIMEFRAME_M10
    M12 = mt5.TIMEFRAME_M12
    M15 = mt5.TIMEFRAME_M15
    M20 = mt5.TIMEFRAME_M20
    M30 = mt5.TIMEFRAME_M30
    H1 = mt5.TIMEFRAME_H1
    H2 = mt5.TIMEFRAME_H2
    H3 = mt5.TIMEFRAME_H3
    H4 = mt5.TIMEFRAME_H4
    H6 = mt5.TIMEFRAME_H6
    H8 = mt5.TIMEFRAME_H8
    H12 = mt5.TIMEFRAME_H12
    D1 = mt5.TIMEFRAME_D1
    W1 = mt5.TIMEFRAME_W1
    MN1 = mt5.TIMEFRAME_MN1

# Trading instruments we're interested in
SYMBOLS = [
    "XAUUSD",
    "BTCUSD",
    "USTEC",
    "US500",
    "US30",
    "AUDUSD"
]

# Data collection settings
DATA_FOLDER = "data/raw"
TIMEFRAMES = [tf for tf in Timeframe]

# Each tick/rate contains these fields by default
TICK_FIELDS = [
    'time', 'bid', 'ask', 'last', 'volume', 
    'time_msc', 'flags', 'volume_real'
]

RATE_FIELDS = [
    'time', 'open', 'high', 'low', 'close', 
    'tick_volume', 'spread', 'real_volume'
]
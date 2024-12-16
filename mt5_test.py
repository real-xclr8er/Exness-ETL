# mt5_test.py

import MetaTrader5 as mt5
from datetime import datetime

def test_mt5_connection():
    """Test MetaTrader5 connection and basic functionality."""
    
    # Initialize MT5 connection
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        return False
    
    # Display connection status
    print("\nConnection Info:")
    print(f"MetaTrader5 package version: {mt5.__version__}")
    
    # Get terminal info
    terminal_info = mt5.terminal_info()
    if terminal_info is not None:
        print("\nTerminal Info:")
        print(f"  Connected: {terminal_info.connected}")
        print(f"  Trade allowed: {terminal_info.trade_allowed}")
        print(f"  Maximum bars in chart: {terminal_info.maxbars}")
        
        if not terminal_info.dlls_allowed:
            print("\nNote: DLL imports are currently disabled.")
            print("This only affects certain automated trading features.")
            print("Basic market data collection and analysis will work normally.")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info is not None:
        print("\nAccount Info:")
        print(f"  Login: {account_info.login}")
        print(f"  Balance: {account_info.balance}")
        print(f"  Currency: {account_info.currency}")
    else:
        print("\nFailed to get account info")
        print(f"Error code: {mt5.last_error()}")
    
    # Test market data access
    print("\nTesting market data access:")
    symbols = mt5.symbols_total()
    if symbols > 0:
        print(f"✓ Successfully connected to market data feed")
        print(f"✓ Total symbols available: {symbols}")
        print("\nSample symbols:")
        for symbol in mt5.symbols_get()[:3]:
            print(f"  {symbol.name}")
            
        # Test data retrieval for first symbol
        first_symbol = mt5.symbols_get()[0].name
        rates = mt5.copy_rates_from(first_symbol, mt5.TIMEFRAME_D1, datetime.now(), 1)
        if rates is not None:
            print(f"\n✓ Successfully retrieved price data for {first_symbol}")
    
    # Clean up
    mt5.shutdown()
    return True

if __name__ == "__main__":
    print("Testing MetaTrader5 connection...")
    test_mt5_connection()
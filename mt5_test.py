# mt5_test.py

import MetaTrader5 as mt5
import pandas as pd
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
        print(f"  Enable DLL: {terminal_info.dlls_allowed}")
        print(f"  Trade allowed: {terminal_info.trade_allowed}")
        print(f"  Maximum bars in chart: {terminal_info.maxbars}")
        print(f"  Community account: {terminal_info.community_account}")
        print(f"  Community connection: {terminal_info.community_connection}")
        
        if not terminal_info.dlls_allowed:
            print("\nWARNING: DLL imports are not allowed!")
            print("Please enable DLL imports in MetaTrader5 settings:")
            print("1. Tools -> Options -> Expert Advisors")
            print("2. Check 'Allow DLL imports'")
            print("3. Restart MetaTrader5")
    
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
    
    # Test symbol availability
    symbols = mt5.symbols_total()
    if symbols > 0:
        print(f"\nTotal symbols available: {symbols}")
        print("First few symbols:")
        for symbol in mt5.symbols_get()[:3]:
            print(f"  {symbol.name}")
    
    # Clean up
    mt5.shutdown()
    return True

if __name__ == "__main__":
    print("Testing MetaTrader5 connection...")
    test_mt5_connection()
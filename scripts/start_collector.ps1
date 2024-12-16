# start_collector.ps1

# Activate virtual environment and start collector
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python background_collector.py"
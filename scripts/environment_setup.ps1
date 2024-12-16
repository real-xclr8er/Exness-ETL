# environment_setup.ps1

# Check if Python 3.10 is available
$pythonCmd = "py -3.10"
$testPython = Invoke-Expression "$pythonCmd --version" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Python 3.10 not found. Please install Python 3.10 from python.org"
    Write-Host "Download link: https://www.python.org/downloads/release/python-3109/"
    exit 1
}

Write-Host "Found: $testPython"

# Create virtual environment directory if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment with Python 3.10..."
    Invoke-Expression "$pythonCmd -m venv venv"
    
    if ($?) {
        Write-Host "Virtual environment created successfully"
    } else {
        Write-Host "Failed to create virtual environment"
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists"
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Verify Python version in virtual environment
python --version

# Install base requirements
Write-Host "Installing base requirements..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Verify MetaTrader5 package installation
python -c "import MetaTrader5 as mt5; print(f'MetaTrader5 package version: {mt5.__version__}')"

Write-Host "Environment setup complete!"
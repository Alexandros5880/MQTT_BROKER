@echo off

echo Checking for Python 3 installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python 3 is not installed. Installing Python 3...
    winget install -e --id Python.Python.3
    if %errorLevel% neq 0 (
        echo Python 3 installation failed. Ensure winget is installed and retry.
        pause
        exit /b
    )
) else (
    echo Python 3 is already installed.
)

echo Checking for NGROK installation...
ngrok --version >nul 2>&1
if %errorLevel% neq 0 (
    echo NGROK is not installed. Installing NGROK...
    winget install -e --id Ngrok.Ngrok
    if %errorLevel% neq 0 (
        echo NGROK installation failed. Ensure winget is installed and retry.
        pause
        exit /b
    )
) else (
    echo NGROK is already installed.
)

echo Starting MQTT Broker...
start pipenv run python mqtt_broker.py

echo Starting ngrok...
start ngrok start --config ngrok.yml --all

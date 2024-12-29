@echo off

echo Checking for winget installation...
winget --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Winget is not installed on this system.
    echo Please install Winget manually from the Microsoft Store or GitHub:
    echo https://github.com/microsoft/winget-cli
    pause
    exit /b
) else (
    echo Winget is already installed.
)

echo Checking for Python 3 installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python 3 is not installed. Installing Python 3...
    winget install -e --id Python.Python.3
    if %errorLevel% neq 0 (
        echo Python 3 installation failed. Ensure winget is properly configured and retry.
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
        echo NGROK installation failed. Ensure winget is properly configured and retry.
        pause
        exit /b
    )
) else (
    echo NGROK is already installed.
)

echo Starting MQTT Broker...
start pipenv run python mqtt_broker.py

echo Starting NGROK...
start ngrok start --config ngrok.yml --all

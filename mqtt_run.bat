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
    winget install --id Python.Python.3.12
    if %errorLevel% neq 0 (
        echo Python 3 installation failed. Ensure winget is properly configured and retry.
        pause
        exit /b
    )
) else (
    echo Python 3 is already installed.
)

echo Checking for Pipenv installation...
pipenv --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Pipenv is not installed. Installing Pipenv...
    pip install pipenv
    if %errorLevel% neq 0 (
        echo Pipenv installation failed. Ensure Python and pip are installed and retry.
        pause
        exit /b
    ) else (
        echo Pipenv installed successfully.
    )
) else (
    echo Pipenv is already installed.
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

:: Change the working directory to the location of the .bat file
cd /d "%~dp0"

:: Confirm the current directory (debugging step)
echo Current Directory: %cd%

echo Starting MQTT Broker...
if exist mqtt_broker.py (
    pipenv run python mqtt_broker.py
    if %errorLevel% neq 0 (
        echo "pipenv run python mqtt_broker.py" failed to run.
        pause
        exit /b
    )
) else (
    echo mqtt_broker.py not found in the current directory.
    pause
    exit /b
)

echo Starting NGROK...
if exist ngrok.yml (
    ngrok start --config ngrok.yml --all
    if %errorLevel% neq 0 (
        echo NGROK failed to start. Ensure ngrok.yml is properly configured.
        pause
        exit /b
    )
) else (
    echo ngrok.yml not found in the current directory.
    pause
    exit /b
)

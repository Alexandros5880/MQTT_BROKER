#!/bin/bash

echo "Checking for Winget installation..."
if ! command -v winget &> /dev/null; then
    echo "Winget is not installed on this system."
    echo "Please install Winget manually from the Microsoft Store or GitHub:"
    echo "https://github.com/microsoft/winget-cli"
    read -p "Press Enter to exit..."
    exit 1
else
    echo "Winget is already installed."
fi

echo "Checking for Python 3 installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing Python 3..."
    winget install --id Python.Python.3.12
    if [ $? -ne 0 ]; then
        echo "Python 3 installation failed. Ensure winget is properly configured and retry."
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    echo "Python 3 is already installed."
fi

echo "Checking for Pipenv installation..."
if ! command -v pipenv &> /dev/null; then
    echo "Pipenv is not installed. Installing Pipenv..."
    pip install pipenv
    if [ $? -ne 0 ]; then
        echo "Pipenv installation failed. Ensure Python and pip are installed and retry."
        read -p "Press Enter to exit..."
        exit 1
    else
        echo "Pipenv installed successfully."
    fi
else
    echo "Pipenv is already installed."
fi

echo "Checking for NGROK installation..."
if ! command -v ngrok &> /dev/null; then
    echo "NGROK is not installed. Installing NGROK..."
    winget install -e --id Ngrok.Ngrok
    if [ $? -ne 0 ]; then
        echo "NGROK installation failed. Ensure winget is properly configured and retry."
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    echo "NGROK is already installed."
fi

# Change the working directory to the location of the script
cd "$(dirname "$0")"

# Confirm the current directory (debugging step)
echo "Current Directory: $(pwd)"

echo "Starting MQTT Broker..."
if [ -f mqtt_broker.py ]; then
    gnome-terminal -- bash -c "pipenv run python mqtt_broker.py; if [ $? -ne 0 ]; then echo 'pipenv run python mqtt_broker.py failed to run'; read -p 'Press Enter to exit...'; fi"
else
    echo "mqtt_broker.py not found in the current directory."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Starting NGROK..."
if [ -f ngrok.yml ]; then
    ngrok start --config ngrok.yml --all
    if [ $? -ne 0 ]; then
        echo "NGROK failed to start. Ensure ngrok.yml is properly configured."
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    echo "ngrok.yml not found in the current directory."
    read -p "Press Enter to exit..."
    exit 1
fi

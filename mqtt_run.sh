#!/bin/bash

# Check for Python 3 installation
echo "Checking for Python 3 installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing Python 3..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3
    elif command -v brew &> /dev/null; then
        brew install python
    else
        echo "Package manager not found. Install Python 3 manually and retry."
        exit 1
    fi
else
    echo "Python 3 is already installed."
fi

# Check for NGROK installation
echo "Checking for NGROK installation..."
if ! command -v ngrok &> /dev/null; then
    echo "NGROK is not installed. Installing NGROK..."
    if command -v apt &> /dev/null; then
        wget -q -O ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
        unzip ngrok.zip -d /usr/local/bin/
        rm ngrok.zip
    elif command -v brew &> /dev/null; then
        brew install --cask ngrok
    else
        echo "Package manager not found. Install NGROK manually and retry."
        exit 1
    fi
else
    echo "NGROK is already installed."
fi

# Start MQTT Broker
echo "Starting MQTT Broker..."
gnome-terminal -- bash -c "pipenv run python mqtt_broker.py; exec bash"

# Start NGROK
echo "Starting NGROK..."
gnome-terminal -- bash -c "ngrok start --config ngrok.yml --all; exec bash"

#!/bin/bash

echo "Starting MQTT Broker..."
gnome-terminal -- bash -c "pipenv run python mqtt_broker.py; exec bash"

echo "Starting ngrok..."
gnome-terminal -- bash -c "ngrok start --config ngrok.yml --all; exec bash"

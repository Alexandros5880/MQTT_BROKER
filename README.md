### Run Windows:
`./mqtt_run.bat`

### Run Linux:
`./mqtt_run.sh`

### RUN MQTT SERVER:
`pipenv run python mqtt_broker.py; exec bash`

### NGROK:
`ngrok start --config ngrok.yml --all`

### Auto start app on windows 10:
Put this file `mqtt_run.bat` into this diractory:
`C:\Users\User\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`
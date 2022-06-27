#!/bin/sh
#python3 driver-defend.py defender01 10.0.2.15:30824
python3 driver-defend.py $CONFIG_FILE $SERVER_IP:$SERVER_PORT

# do a reset on exit
if [ $RESET == true ]; then
    curl http://$SERVER_IP:$SERVER_PORT/v1/commands/reset -X POST
fi

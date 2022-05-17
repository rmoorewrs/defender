#!/bin/sh
#python3 driver-attack.py attacker01 10.0.2.15:30824
python3 driver-attack.py $OBJECT_NAME $SERVER_IP:$SERVER_PORT

# do a reset on exit
if [ $RESET == true ]; then
    curl http://$SERVER_IP:$SERVER_PORT/v1/commands/reset -X POST
fi

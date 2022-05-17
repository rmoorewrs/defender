#!/bin/sh
python3 driver-attack.py attacker01 10.0.2.15:30824
#python3 driver-attack.py attacker01 172.17.0.3:5000

# do a reset on exit
curl http://10.0.2.15:30824/v1/commands/reset -X POST

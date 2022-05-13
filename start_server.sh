#!/bin/sh
# run the multicast advertiser and the rest-api server

# set the IP of the default route and default port for rest server
IP=$(ip route | awk '!/default/{print $9}')
PORT=5000
python3 server_ip_multicast.py send $IP $PORT &

# start rest server
python3 worldmodel.py
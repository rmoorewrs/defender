 - bash one-liner to get IP address, for server_ip_multicast advertiser
 ```
 IP=$(ip route | awk '!/default/{print $9}')
 server_ip_multicast.py send $IP 5000 &
 ```


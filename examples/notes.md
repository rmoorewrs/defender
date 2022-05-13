 - bash one-liner to get IP address, for server_ip_multicast advertiser
 ```
 IP=$(ip route | awk '!/default/{print $9}')
 server_ip_multicast.py send $IP 5000 &
 ```

- find IP address of docker container
multiple methods
```
1) $ docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container-ID>

2) $ docker inspect <containerID> | grep "IPAddress"
```

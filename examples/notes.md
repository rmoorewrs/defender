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

### Root cause of why switching to newer python3, flask and requests library broke the rest API
- See [stack overflow about bad requests with flask](https://stackoverflow.com/questions/71794902/issue-with-bad-request-syntax-with-flask)
- apparently, newer version of requests library (in LTS21) requires a 'location' in the request parser
    - older version works fine without specifying location
    - newer version requires ```location='form'``` to be added to `add_argument` method

Old version:
```
obj_parser = reqparse.RequestParser()
obj_parser.add_argument('id', type=str,help='each object has a unique ID')
```

New version:
```
obj_parser = reqparse.RequestParser()
obj_parser.add_argument('id', type=str,help='each object has a unique ID',location='form')
```

Note: parsing a query string, you have to use location='args' instead of 'form'
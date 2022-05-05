# JS Renderer

This renderer uses PIXI.js and a collection of PNG sprites to render the world state in the browser. Launch the view by executing

```bash

jcalvert@jcalvert-windriver:/opt/workspaces/gh/defender/renderer$ ./serve.sh 
127.0.0.1 - - [05/May/2022 10:02:15] "GET /js/map-item.js HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:02:15] "GET /js/map-manager.js HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:02:15] code 404, message File not found
127.0.0.1 - - [05/May/2022 10:02:15] "GET /favicon.ico HTTP/1.1" 404 -
127.0.0.1 - - [05/May/2022 10:03:41] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:03:41] "GET /js/map-item.js HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:03:41] "GET /js/map-manager.js HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:03:41] code 404, message File not found
127.0.0.1 - - [05/May/2022 10:03:41] "GET /favicon.ico HTTP/1.1" 404 -
127.0.0.1 - - [05/May/2022 10:03:41] "GET /assets/tanks/panzer.png HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:04:17] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:04:17] "GET /js/map-item.js HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:04:17] "GET /js/map-manager.js HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:04:17] code 404, message File not found
127.0.0.1 - - [05/May/2022 10:04:17] "GET /favicon.ico HTTP/1.1" 404 -
127.0.0.1 - - [05/May/2022 10:04:17] "GET /assets/tanks/sherman.png HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:05:32] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:05:32] "GET /js/map-manager.js HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:21:07] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:21:07] "GET /js/map-item.js HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:21:07] "GET /js/map-manager.js HTTP/1.1" 200 -
127.0.0.1 - - [05/May/2022 10:21:07] code 404, message File not found
127.0.0.1 - - [05/May/2022 10:21:07] "GET /favicon.ico HTTP/1.1" 40
.... snip ....


```

and exit with Ctrl-C.  The map will be available at [http://localhost:5001/](http://localhost:5001/)



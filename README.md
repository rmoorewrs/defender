# Defender

This is a simple defender simulation demo intended to run on a container-based platform like Docker or Kubernetes. The application is fully distributed and each component can run in its own container or on an embedded target. By design, the components have no specific hardware, OS or language requirements.

The purpose of the app is to provide something to run as a demo that's more interesting than the standard 'hello world'. The point is to have distributed components interacting in a way that's easy to visualize and understand. 

![](images/defender-diagram2.png)

The world-model is a simple database that keeps track of all objects in the simulated world. Interaction with the world-model is via a RESTful API and beyond detecting collisions between objects, the world-model doesn't actively do anything on its own. 

Rules of the simulation: attackers try to reach the target, defenders try to stop them and obstacles get in the way. When objects collide, they die. The exception are obstacles, which survive collision. Once dead, objects don't cause further collisions.

If an attacker collides with the target (round flying saucer at the top in this implementation), the simulation is over. When objects collide, they die. The exception are obstacles, which survive collision. Once dead, objects don't cause further collisions.

Each object needs an agent or driver program to move it around in the world, so the intent is to have one object driver (control program) per container which controls one object in the world model. 

This is not about efficiency -- in a real video game or simulation, all of the actors would be typically combined into one program. The goal here is to demonstrate distributed appliations interacting on an embedded, containerized or hybrid compute platform (hybrid meaning some parts running in containers, others on embedded targets) -- so the "distributed" part has been maximized intentionally.

Rendering is done in a browser where a JavaScript program reads and renders the state of the world by polling the world-model.

The scenario can easily be changed by providing a different set of sprite graphics.

![](images/collision-avoidance.gif)


Package requirements:
```
sudo apt install python3 python3-flask python3-flask-restful python3-flask-cors
```

## 1) First start the world-model server and the server address advertiser
```
$ python3 world-model.py
$ python3 server_ip_multicast.py send <rest_server_ip> <rest_server_port>

example:
    python3 server_ip_multicast.py send 10.10.11.56 5000
```
The server_ip_multicast.py can be started as a receiver to test the multicast message
```
$ python3 server_ip_multicast.py recv
```
## 2) Start the renderer
```
cd renderer
 ./serve.sh 
```
Exit with Ctrl-C.  The map will be available at [http://localhost:5001/](http://localhost:5001/)

## 3) Start the Object Drivers
Example "Driver" or agents are available in the top directory (driver-*.py). The drivers take the name of an active object as an argument and a second argument that specifies either what IP and port (e.g. 172.17.0.3:5000) or "multicast" to try and detect the address of the world server. 

The driver will then begin to move that object around in the 2D world map. If the object collides with something, it will die and the driver program will exit.
```
$ python3 driver-circle.py attacker01 [IP:Port | multicast]
```

Look in `init-world.json` to see the default list of objects the world starts with, or use 
```
$ curl http://<server_ip_address>:<port>/v1/objects/
```
to get a list of all objects in the world. 

The ultimate goal is to create controllers that manage the creation and deletion of actors in the simulation.

------

# Running from Containers
The OCI folder contains recipes for a base image and other container images that are derived from the base. These are the server (i.e. world_model.py), the renderer and the object drivers.

See [OCI/README.md](https://github.com/rmoorewrs/defender/blob/master/OCI/README.md) for more details.

------

# REST API Documentation

### Get and Set boundaries of world model
Get Boundaries:
```
$ curl http://127.0.0.1:5000/v1/parameters/bounds/
```
Set Boundaries:
```
$ curl http://127.0.0.1:5000/v1/parameters/bounds/ -X PUT -d "xmax=2048&ymax=1536"
```

### Get a list of objects
```
$ curl http://127.0.0.1:5000/v1/objects/
```

### Get a list of objects by type (attacker,defender,obstacle,target)
```
$ curl http://127.0.0.1:5000/v1/objects/type/defender
```

### Get a specific object by index
```
$ curl http://127.0.0.1:5000/v1/objects/3
```

### Get a specific object by name (names must be unique)
```
$ curl http://localhost:5000/v1/objects/name/attacker01
```

### Add an object with POST (name must not already exist)
```
$ curl http://localhost:5000/v1/objects/name/obstacle05 -X POST -d "name=obstacle05&x=200&y=200&ype=obstacle"
```

### Update an object's parameters with PUT (name must exist)
```
$ curl -d "x=31&y=11" -X PUT http://localhost:5000/v1/objects/name/defender02
```
Valid parameters are:
|Param Name|Note|
|----------|----|
|id       | uuid, unique
|name     | name, unique|
|type     | object type: attacker,defender,obstacle,target|
|x        | x cooridnate in units|
|y        | y coordinate in units|
|radius   | object radius in units|
|rotation | rotational angle or heading, degrees|
|speed    | speed in units/sec |
|state    | object state: active, dead|
    
All distance parameters are in arbitrary units... adjust per the simulation scenario


### Delete an object with DELETE
```
$ curl -X DELETE http://127.0.0.1:5000/v1/objects/6
$ curl -X DELETE http://127.0.0.1:5000/v1/objects/name/attacker01
```

### Reset the world model back to contents of init-world.json
```
$ curl http://localhost:5000/v1/commands/reset -X POST
```

### Dump the world-model objects into a json file
```
$ curl http://10.10.11.56:5000/v1/commands/dump -X POST -d "filename=test01.json"
```

### get a sensor scan seen by a named object
```
$ curl http://localhost:5000/v1/sensors/name/attacker01?scanrange=200 -X GET
```

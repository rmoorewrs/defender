# defender
This is a simple defender simulation demo intended to run on a container-based platform like Docker or Kubernetes. The application is fully distributed and each component can be run in its own container or on an embedded target. By design, the components have no specific hardware, OS or language requirements.

The purpose of the app is to provide something to run as a demo that's more interesting than the standard 'hello world'. The point is to have distributed components interacting in a way that's easy to visualize and understand. 

Here's the scenario: attackers are trying to reach a target, defenders are trying to prevent that from happening and obstacles get in the way. If an attacker reaches the target, the simulation is over. If objects collide, they die (except obstacles, which survive collisions). 

![](images/scenario.png)

The world-model is a simple database that keeps track of all objects in the simulated world. Interaction with the world-model is via a RESTful API and beyond detecting collisions between objects, the world-model doesn't actively do anything. 

Each object needs an agent or driver program to move it around in the world. Each object will have an driver program that controls it's movement. In a typical video game, all of the actors would be combined for efficiency, but the goal here is to enable distributed appliations interacting on an embedded, containerized or hybrid computing platform.

Rendering is done in a browser where a JavaScript program reads and renders the state of the world by polling the world-model.


![](images/defender-diagram.png)


Package requirements:
```
sudo apt install python3 python3-flask python3-flask-restful python3-flask-cors
```

First start the world-model server
```
python3 world-model.py
```

Then start the renderer
```
cd renderer
 ./serve.sh 
```
and exit with Ctrl-C.  The map will be available at [http://localhost:5001/](http://localhost:5001/)

A sample "Driver" or agent is available in `./sample-driver`. The driver takes the name of an object and then begins to move it around in the 2D world map.
```
cd sample-driver
python3 attacker01
```
Look in `init-world.json` to see the default list of objects the world starts with

## REST API - rough documentation


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
|x        | x cooridnate|
|y        | y coordinate|
|radius   | object radius|
|rotation | rotational angle, degrees|
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

### get a sensor scan seen by a named object
```
$ curl http://localhost:5000/v1/sensors/name/attacker01?scanrange=200 -X GET
```
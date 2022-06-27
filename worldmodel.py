from cmath import sqrt
from distutils.log import error
from fileinput import filename
from operator import index
import string
from turtle import heading
from unicodedata import name
from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
import uuid
import json
from math import sqrt
from flask_cors import CORS


# based on example from https://medium.com/duomly-blockchain-online-courses/how-to-create-a-simple-rest-api-with-python-and-flask-in-5-minutes-94bb88f74a23
# to exercise with curl:
#
#       Get world model boundaries
#       $ curl http://localhost:5000/v1/parameters/bounds/
#
#       Get a list of objects
#       $ curl http://127.0.0.1:5000/v1/objects/
#
#       Get a list of objects by type
#       $ curl http://127.0.0.1:5000/v1/objects/type/defender
#
#       Get a specific object by index
#       $ curl http://127.0.0.1:5000/v1/objects/3
#
#       Get a specific object by name
#       $ curl http://localhost:5000/v1/objects/name/attacker01
#
#       add an object with POST
#       $ curl http://localhost:5000/v1/objects/name/obstacle05 -X POST -d 'name=obstacle05&x=200&y=200&type=obstacle'
#
#       update an object with PUT
#       $ curl -d 'x=31&y=11' -X PUT http://localhost:5000/v1/objects/name/defender02
#
#       delete an object with DELETE
#       $ curl -X DELETE http://127.0.0.1:5000/v1/objects/name/attacker01
#
#       reset the world model back to contents of init-world.json
#       $ curl http://localhost:5000/v1/commands/reset -X POST
#
#       Dump the world-model objects into a json file
#       $ curl http://10.10.11.56:5000/v1/commands/dump -X POST -d 'filename=test01.json'
#
#       scan for objects relative to named object
#       $ curl http://localhost:5000/v1/sensors/name/attacker01?scanrange=200 -X GET


# Some defaults
DEFAULT_CONFIG_FILE = "config/init-world.json"


# set up RESTful API app
app = Flask(__name__)
CORS(app)
api = Api(app)


def are_two_points_in_range(x1, y1, x2, y2, range):
    distance = sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
    if distance <= range:
        return True
    else:
        return False


# classes for handling objects in the world -- these are persistent for as long as the program runs
class WorldObject:
    def __init__(
        self,
        name: str,
        type: str,
        x: float,
        y: float,
        radius: float,
        rotation: float,
        speed: float,
        state: str,
        id: str = None,
    ) -> None:
        if id == "None" or id == None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id
        self.name = name
        self.type = type
        self.x = x
        self.y = y
        self.radius = radius
        self.rotation = rotation
        self.speed = speed
        if state == None:
            self.state = "active"
        else:
            self.state = state

    def serialize(self):
        json_obj = {
            "id": str(self.id),
            "name": str(self.name),
            "type": self.type,
            "x": float(self.x),
            "y": float(self.y),
            "radius": float(self.radius),
            "rotation": float(self.rotation),
            "speed": float(self.speed),
            "state": self.state,
        }
        return json_obj

    def get(self):
        return self.serialize()


class WorldObjectList:
    def __init__(self, filename: str = DEFAULT_CONFIG_FILE) -> None:
        self.object_list = []
        self.read_config_from_file(filename)

    def read_config_from_file(self, filename: str = DEFAULT_CONFIG_FILE):
        with open(filename) as file:
            config_dict = json.load(file)
            if config_dict:
                for each in config_dict:
                    self.object_list.append(
                        WorldObject(
                            each["name"],
                            each["type"],
                            each["x"],
                            each["y"],
                            each["radius"],
                            each["rotation"],
                            each["speed"],
                            each["state"],
                            each["id"],
                        )
                    )
                # check to see if we have any initial collisions
                self.update_collisions()
            else:
                print("No objects in file " + filename)
                return None

    def print(self):
        for each in self.object_list:
            print(each.serialize())
            print(",")

    def get_list(self):
        return_list = []
        for each in self.object_list:
            return_list.append(each.serialize())
        return return_list

    def get_id(self, id):
        for each in self.WorldObjectList:
            if id == each.id:
                return each

    # this should be called every time an object changes x,y or radius
    # [TODO] obstacles shouldn't die in collision
    def update_collisions(self):
        # go through the list of objects and check against collisions with  remaining objects
        list = self.object_list
        list_len = len(self.object_list)
        for i in range(0, list_len):
            for j in range(i + 1, list_len):
                # compute distance between points
                a = list[i]
                b = list[j]
                # An object has to be alive to participate in a collision
                if a.state == "dead" or b.state == "dead":
                    continue

                # check to see objects are in collision range
                if (
                    are_two_points_in_range(a.x, a.y, b.x, b.y, a.radius + b.radius)
                    == True
                ):
                    # we have a collision, mark any non-obstacle parties(Obstacles don't die in a collision)
                    print("Collision Detected")
                    if a.type != "obstacle":
                        a.state = "dead"
                    if b.type != "obstacle":
                        b.state = "dead"


# Create global list of objects in the world -- REST API instances will reference this
GLOBAL_OBJECT_LIST = WorldObjectList(DEFAULT_CONFIG_FILE)

##########################################
# Resource class for world map parameters
##########################################

# default world map boundaries
DEFAULT_XMAX = 1024
DEFAULT_XMIN = 0
DEFAULT_YMAX = 768
DEFAULT_YMIN = 0

param_parser = reqparse.RequestParser()
param_parser.add_argument(
    "xmax", type=float, help="maximum x limit on world map", location="form"
)
param_parser.add_argument(
    "xmin", type=float, help="minimum x limit on world map", location="form"
)
param_parser.add_argument(
    "ymax", type=float, help="maximum y limit on world map", location="form"
)
param_parser.add_argument(
    "ymin", type=float, help="minimum y limit on world map", location="args"
)


class WorldLimits(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.xmax = DEFAULT_XMAX
        self.ymax = DEFAULT_YMAX
        self.xmin = DEFAULT_XMIN
        self.ymin = DEFAULT_YMIN

    def serialize(self):
        return [
            {"xmax": self.xmax},
            {"xmin": self.xmin},
            {"ymax": self.ymax},
            {"ymin": self.ymin},
        ]

    def get(self):
        return self.serialize(), 200

    def put(self):
        args = param_parser.parse_args()
        self.xmax = args["xmax"] if args["xmax"] is not None else self.xmax
        self.xmin = args["xmin"] if args["xmin"] is not None else self.xmin
        self.ymax = args["ymax"] if args["ymax"] is not None else self.ymax
        self.ymin = args["ymin"] if args["ymin"] is not None else self.ymin
        return self.serialize(), 200


##########################################
# Resource classes for world objects - Classes, functions and variables for implementing the REST API
##########################################

# set up parser for requests related to objects
obj_parser = reqparse.RequestParser()
obj_parser.add_argument(
    "id", type=str, help="each object has a unique ID", location="form"
)
obj_parser.add_argument(
    "name", type=str, help="each object must have a unique name", location="form"
)
obj_parser.add_argument(
    "type",
    type=str,
    help="Type of object (target,attacker,defender,obstacle)",
    location="form",
)
obj_parser.add_argument("x", type=float, help="X coordinate of object", location="form")
obj_parser.add_argument("y", type=float, help="Y coordinate of object", location="form")
obj_parser.add_argument(
    "radius", type=float, help="Radius of object in meters", location="form"
)
obj_parser.add_argument(
    "rotation", type=float, help="Angle of object in degrees", location="form"
)
obj_parser.add_argument(
    "speed", type=float, help="Speed of object in meters/second", location="form"
)
obj_parser.add_argument(
    "state", type=str, help="State of of object (active,dead", location="form"
)


# resource_fields = {
#     'id':    fields.String,
#     'name':    fields.String,
#     'type':   fields.String,
#     'x' : fields.Float,
#     'y' : fields.Float,
#     'radius' : fields.Float,
#     'rotation' : fields.Float,
#     'speed': fields.Float,
#     'state' : fields.String,
# }


class AllObjects(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list = GLOBAL_OBJECT_LIST

    def get(self):
        result = self.list.get_list()
        return result, 200


class AllObjectsByType(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list = GLOBAL_OBJECT_LIST

    def get(self, type):
        list = self.list.get_list()
        result = []
        for each in list:
            if each["type"] == type:
                result.append(each)
        return result, 200


class ObjectByIndex(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list = GLOBAL_OBJECT_LIST

    def get(self, obj_index):
        if obj_index < len(self.list.object_list):
            obj = self.list.object_list[obj_index]
            return obj.serialize()
        else:
            abort(404, message="index {} not found".format(obj_index))


class ObjectById(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list = GLOBAL_OBJECT_LIST

    def abort_if_id_exists(self, id):
        for each in self.list.object_list:
            if each.id == id:
                abort(409, message="id {} already exists".format(id))

    def abort_if_id_doesnt_exist(self, id):
        for each in self.list.object_list:
            if each.id == id:
                return each
        # if you made it here, there was no match
        abort(404, message="id {} doesn't exist".format(id))

    def get(self, obj_id):
        list = self.list.object_list
        match = self.abort_if_id_doesnt_exist(obj_id)
        return match.serialize()

    def delete(self, obj_id):
        match = self.abort_if_id_doesnt_exist(obj_id)
        self.list.object_list.remove(match)
        return "", 202


class ObjectByName(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list = GLOBAL_OBJECT_LIST

    def abort_if_name_exists(self, name):
        for each in self.list.object_list:
            if each.name == name:
                abort(409, message="name {} already exists".format(name))

    def abort_if_name_doesnt_exist(self, name):
        for each in self.list.object_list:
            if each.name == name:
                return each
        # if you made it here, there was no match
        abort(404, message="name {} doesn't exist".format(name))

    def get(self, name):
        for each in self.list.object_list:
            if each.name == name:
                return each.serialize()
        # if we made it here, no id match was found
        abort(404, message="name {} not found".format(name))

    # use the post method to create a new object
    def post(self, name):
        args = obj_parser.parse_args()
        self.abort_if_name_exists(name)

        # name doesn't exist, create object and append to the list
        new_obj = WorldObject(
            name,
            args["type"],
            args["x"],
            args["y"],
            args["radius"],
            args["rotation"],
            args["speed"],
            args["state"],
            None,
        )
        self.list.object_list.append(new_obj)
        return new_obj.serialize(), 200

    # use the put method to update an existing object. You can update x,y,radius and state
    def put(self, name):
        args = obj_parser.parse_args()
        # find named object
        match = self.abort_if_name_doesnt_exist(name)
        match.x = args["x"] if args["x"] is not None else match.x
        match.y = args["y"] if args["y"] is not None else match.y
        match.radius = args["radius"] if args["radius"] is not None else match.radius
        match.rotation = (
            args["rotation"] if args["rotation"] is not None else match.rotation
        )
        match.speed = args["speed"] if args["speed"] is not None else match.rotation
        match.state = args["state"] if args["state"] is not None else match.state

        # check for collisions since we might've changed position or radius
        self.list.update_collisions()
        return match.serialize()

    def delete(self, name):
        match = self.abort_if_name_doesnt_exist(name)
        self.list.object_list.remove(match)
        return "", 202


##########################################
# Resource class for sensors objects
##########################################
sensor_parser = reqparse.RequestParser()
sensor_parser.add_argument(
    "scanrange", type=float, help="Range of scan to perform in meters", location="args"
)


class SensorByName(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list = GLOBAL_OBJECT_LIST

    def abort_if_id_doesnt_exist(self, name):
        for each in self.list.object_list:
            if each.name == name:
                return each
        # if you made it here, there was no match
        abort(404, message="name {} doesn't exist".format(name))

    def get(self, name):
        scan = []
        args = sensor_parser.parse_args()
        # get the WorldObject with the right name
        match = self.abort_if_id_doesnt_exist(name)
        list = self.list.object_list
        list_len = len(list)
        for i in range(0, list_len):
            a = list[i]
            b = match
            # don't match yourself
            if a.name != b.name:
                if (
                    are_two_points_in_range(a.x, a.y, b.x, b.y, args["scanrange"])
                    == True
                ):
                    scan.append(a.serialize())
        return scan, 200


##########################################
# Resource class for management commands
##########################################

# set up command parser
cmd_parser = reqparse.RequestParser()
cmd_parser.add_argument(
    "filename",
    type=str,
    help="dump the state of the world to a file called <filename>",
    location="form",
)


class ManagementCommands(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list = GLOBAL_OBJECT_LIST

    def post(self, command):
        global GLOBAL_OBJECT_LIST
        args = cmd_parser.parse_args()
        if command == "reset":
            GLOBAL_OBJECT_LIST = WorldObjectList(DEFAULT_CONFIG_FILE)
            return {"reset": "True"}, 200
        elif command == "dump":
            with open(args["filename"], "w") as file:
                list = GLOBAL_OBJECT_LIST.get_list()
                jlist = json.dumps(list)
                file.write(jlist)
            return {"dump": args["filename"]}
        return {"response": "Command not found"}, 404


##########################################
# main
##########################################

if __name__ == "__main__":
    # add api endpoints
    # return json list of world limits
    api.add_resource(WorldLimits, "/v1/parameters/bounds/")
    # return json list of all objects in the world
    api.add_resource(AllObjects, "/v1/objects/")
    # get a list of objects based on type
    api.add_resource(AllObjectsByType, "/v1/objects/types/<type>")
    # get a single object based on list index
    api.add_resource(ObjectByIndex, "/v1/objects/index/<int:obj_index>")
    # get a single object based on id
    api.add_resource(ObjectById, "/v1/objects/id/<obj_id>")
    # get/post/put/delete a single object based on name
    api.add_resource(ObjectByName, "/v1/objects/name/<name>")
    # get a sensor reading from a named object
    api.add_resource(SensorByName, "/v1/sensors/name/<name>")
    # implement some management commands
    api.add_resource(ManagementCommands, "/v1/commands/<command>")

    app.run(debug=True, host="0.0.0.0")

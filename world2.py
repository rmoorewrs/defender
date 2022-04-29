from distutils.log import error
from fileinput import filename
from operator import index
import string
from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal_with,abort
import uuid
import json


# based on example from https://medium.com/duomly-blockchain-online-courses/how-to-create-a-simple-rest-api-with-python-and-flask-in-5-minutes-94bb88f74a23
# to exercise with curl:
#       Get a list of objects
#       $ curl http://127.0.0.1:5000/v1/objects/
#
#       Get a specific object
#       $ curl http://127.0.0.1:5000/v1/objects/3
#
#       add an object with POST
#       $ curl -d "uuid=0006&type=defender&x=100&y=100" -X POST http://127.0.0.1:5000/v1/objects/
#
#       update an object with PUT
#       $ curl -d "x=200" -X PUT http://127.0.0.1:5000/v1/objects/6
#
#       delete an object with DELETE
#       $ curl -X DELETE http://127.0.0.1:5000/v1/objects/6



# set up RESTful API app
app = Flask(__name__)
api = Api(app)


# classes for handling objects in the world -- these are persistent for as long as the program runs  
class world_object():
    def __init__(self,name:str,type:str,x:int,y:int,radius:int,state:str,obj_id:str=None) -> None:
        if obj_id=='None' or obj_id==None:
            self.uuid=uuid.uuid4()
        else:
            self.uuid=obj_id
        self.name=name
        self.type=type
        self.x=x
        self.y=y
        self.radius=radius
        self.state=state
    
    def serialize(self):
        json_obj= {
            "uuid":str(self.uuid),
            "name":str(self.name),
            "type":self.type,
            "x":str(self.x),
            "y":str(self.y),
            "radius":str(self.radius),
            "state":self.state
        }
        return json_obj

    def get(self):
        return self.serialize()

class world_object_list():
    def __init__(self,filename:str="init-world.json") -> None:
        self.object_list=[]
        self.read_config_from_file(filename)

    def read_config_from_file(self,filename:str="init-world.json"):
        with open(filename) as file:
            config_dict = json.load(file)
            if config_dict:
                for each in config_dict:
                    self.object_list.append(world_object(each['name'],each['type'], each['x'], each['y'], each['radius'], each['state'],each['obj_id']))
            else:
                print ('No objects in file ' + filename)
                return None
            
    def print(self):
        for each in self.object_list:
            print(each.serialize())
            print(",")

    def get_list(self):
        return_list=[]
        for each in self.object_list:
            return_list.append(each.serialize())
        return return_list

    def get_uuid(self,uuid):
        for each in self.world_object_list:
            if uuid==each.uuid:
                return each


# Create global list of objects in the world -- REST API instances will reference this
GLOBAL_OBJECT_LIST=world_object_list("init-world.json")



# Classes, functions and variables for implementing the REST API
obj_parser = reqparse.RequestParser()
obj_parser.add_argument('obj_id', type=str,help='each object has a unique ID')
obj_parser.add_argument('name', type=str,help='each object must have a unique name')
obj_parser.add_argument('type',type=str,help='Type of object (target,attacker,defender,obstacle)')
obj_parser.add_argument('x',type=int,help='X coordinate of object')
obj_parser.add_argument('y,',type=int,help='Y coordinate of object')
obj_parser.add_argument('radius,',type=int,help='Radius of object in meters')
obj_parser.add_argument('state,',type=str,help='State of of object (init,active,dead')

resource_fields = {
    'obj_id':    fields.String,
    'name':    fields.String,
    'type':   fields.String,
    'x' : fields.Integer,
    'y' : fields.Integer,
    'radius' : fields.Integer,
    'state' : fields.String,
}


class all_objects(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list=GLOBAL_OBJECT_LIST

    def get(self):
        result=self.list.get_list()
        return result,200


class object_by_index(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list=GLOBAL_OBJECT_LIST

    def get(self, obj_index):
        if obj_index < len(self.list.object_list):
            obj=self.list.object_list[obj_index]
            return (obj.serialize())
        else:
            abort(404,message="index {} not found".format(obj_index))


class object_by_uuid(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list=GLOBAL_OBJECT_LIST

    def get(self, obj_uuid):
        list=self.list.object_list
        for each in list:
            if str(each.uuid) == obj_uuid:
                return (each.serialize())
        # if we made it here, no uuid match was found
        abort(404,message="uuid {} not found".format(obj_uuid))


class object_by_name(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list=GLOBAL_OBJECT_LIST

    def get(self, obj_name):
        list=self.list.object_list
        for each in list:
            if each.name == obj_name:
                return (each.serialize())
        # if we made it here, no obj_id match was found
        abort(404,message="name {} not found".format(obj_name))


class hello(Resource):
    def get(self,hello_string):
        return {'hello_string' :  hello_string}

    #def put(self, world_object_id):
    #    parser.add_argument("uuid")
    #    parser.add_argument("type")
    #    parser.add_argument("x")
    #    parser.add_argument("y")
    #    parser.add_argument("radius")
    #    parser.add_argument("state")
    #    args = parser.parse_args()
    #    if world_object_id not in world_objects:
    #        world_object_id = int(max(world_objects.keys())) + 1
    #    else:
    #        world_object = world_objects[world_object_id]
    #        world_object["uuid"] = args["uuid"] if args["uuid"] is not None else world_object["uuid"]
    #        world_object["type"] = args["type"] if args["type"] is not None else world_object["type"]
    #        world_object["x"] = args["x"] if args["x"] is not None else world_object["x"]
    #        world_object["y"] = args["y"] if args["y"] is not None else world_object["y"]
    #        world_object["radius"] = args["radius"] if args["radius"] is not None else world_object["radius"]
    #        world_object["state"] = args["state"] if args["state"] is not None else world_object["state"]
    #        return world_object, 200

    #def delete(self, world_object_id):
    #    if world_object_id not in world_objects:
    #        return "Not found", 404
    #    else:
    #        del world_objects[world_object_id]
    #        return '', 204



#def post(self):
#    parser.add_argument("uuid")
#    parser.add_argument("type")
#    parser.add_argument("x")
#    parser.add_argument("y")
#    parser.add_argument("radius")
#    parser.add_argument("state")
#    args = parser.parse_args()
#    world_object_id = int(max(world_objects.keys())) + 1
#    world_object_id = '%i' % world_object_id
#    world_objects[world_object_id] = {
#        "uuid": args["uuid"],
#        "type": args["type"],
#        "x": args["x"],
#        "y": args["y"],
#        "radius": args["radius"],
#        "state" : args["state"]
#    }
#    return world_objects[world_object_id], 201


if __name__ == "__main__":
    #print ('GLOBAL_OBJECT_LIST:')
    #GLOBAL_OBJECT_LIST.print()
    
    #objlist = world_object_list("init-world.json")
    #print(objlist.get_list())

    api.add_resource(all_objects, '/v1/objects/')
    api.add_resource(object_by_index, '/v1/objects/index/<int:obj_index>')
    api.add_resource(object_by_uuid, '/v1/objects/uuid/<obj_uuid>')
    api.add_resource(hello, '/v1/objects/hello/<hello_string>')
    
    app.run(debug=True)

    
    
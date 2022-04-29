from flask import Flask
from flask_restful import Resource, Api, reqparse
import uuid
import json

app = Flask(__name__)
api = Api(app)

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


# initial list of world model objects
init_world_objects = {
    '1': {'uuid': '0001', 'type': 'attacker', 'x': 10, 'y': 10, 'radius': 1, 'state' : 'active'},
    '2': {'uuid': '0002', 'type': 'attacker', 'x': 10, 'y': 20, 'radius': 1, 'state' : 'active'},
    '3': {'uuid': '0003', 'type': 'defender', 'x': 20, 'y': 10, 'radius': 1, 'state' : 'active'},
    '4': {'uuid': '0004', 'type': 'defender', 'x': 30, 'y': 10, 'radius': 1, 'state' : 'active'},
    '5': {'uuid': '0005', 'type': 'target', 'x': 40, 'y': 10, 'radius': 1, 'state' : 'active'},
    '6': {'uuid': '0006', 'type': 'obstacle', 'x': 20, 'y': 20, 'radius': 10, 'state' : 'active'},
}

parser = reqparse.RequestParser()

class world_object(Resource):
    def __init__(self,type:str,x:int,y:int,radius:int,state:str) -> None:
        super().__init__()
        self.uuid=uuid.uuid4()
        self.type=type
        self.x=x
        self.y=y
        self.radius=radius
        self.state=state
    
    def serialize(self):
        json_obj= {
            "uuid":self.uuid,
            "type":self.type,
            "x":str(self.x),
            "y":str(self.y),
            "radius":str(self.radius),
            "state":self.state
        }
        return json_obj

    def get(self,index):
        return self.serialize()
    
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


class world_object_list(Resource):
    def __init__(self,init_dict) -> None:
        super().__init__()
        self.object_list=[]
        for each in init_dict:
            self.object_list.append(world_object(each['type'], each['x'], each['y'], each['radius'], each['state']))
    
    def print(self):
        for each in self.object_list:
            print(each.serialize())
            print(",")

    def get(self):
        json_obj=None
        for each in self.world_oject_list:
            json_obj.append(each.serialize())
        return self.world_object_list

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



def read_init_config(filename:str="init-world.json"):
    with open(filename) as file:
        return json.load(file)

#api.add_resource(world_object_list, '/v1/objects/')
#api.add_resource(world_object, '/v1/objects/<world_object_index>')
#api.add_resource(world_object, '/v1/objects/<string:uuid>')


if __name__ == "__main__":
    init_dict = read_init_config("init-world.json")
    print ('file returns:')
    print (init_dict)

    list = world_object_list(init_dict)
    print('World Object List now contains:')
    list.print()

    api.add_resource(list, '/v1/objects/')
    app.run(debug=True)

    
    
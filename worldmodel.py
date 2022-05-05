from cmath import sqrt
from distutils.log import error
from fileinput import filename
from operator import index
import string
from unicodedata import name
from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal_with,abort
import uuid
import json
from math import sqrt
from flask_cors import CORS



# based on example from https://medium.com/duomly-blockchain-online-courses/how-to-create-a-simple-rest-api-with-python-and-flask-in-5-minutes-94bb88f74a23
# to exercise with curl:
#       Get a list of objects
#       $ curl http://127.0.0.1:5000/v1/objects/
#
#       Get a specific object
#       $ curl http://127.0.0.1:5000/v1/objects/3
#
#       add an object with POST
#       $ curl -d "id=0006&type=defender&x=100&y=100" -X POST http://127.0.0.1:5000/v1/objects/
#       $ curl -d "type=obstacle&name=obstacle02&x=200&y=200&radius=40" -X POST http://localhost:5000/v1/objects/name/
#
#       update an object with PUT
#       $ curl -d "x=31&y=11" -X PUT http://localhost:5000/v1/objects/name/defender02
#
#       delete an object with DELETE
#       $ curl -X DELETE http://127.0.0.1:5000/v1/objects/6



# set up RESTful API app
app = Flask(__name__)
CORS(app)
api = Api(app)



def are_two_points_in_range(x1, y1, x2, y2, range):
    distance = sqrt( (x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))
    if distance <= range:
        return True
    else:
        return False


# classes for handling objects in the world -- these are persistent for as long as the program runs  
class world_object():
    def __init__(self,name:str,type:str,x:int,y:int,radius:int,state:str,id:str=None) -> None:
        if id=='None' or id==None:
            self.id=uuid.uuid4()
        else:
            self.id=id
        self.name=name
        self.type=type
        self.x=x
        self.y=y
        self.radius=radius
        if state==None:
            self.state='init'
        else:
            self.state=state
    
    def serialize(self):
        json_obj= {
            "id":str(self.id),
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
                    self.object_list.append(world_object(each['name'],each['type'], each['x'], each['y'], each['radius'], each['state'],each['id']))
                # check to see if we have any initial collisions
                self.update_collisions()
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

    def get_id(self,id):
        for each in self.world_object_list:
            if id==each.id:
                return each

    # this should be called every time an object changes x,y or radius
    def update_collisions(self):
        # go through the list of objects and check against collisions with  remaining objects
        list=self.object_list
        list_len=len(self.object_list)
        for i in range(0,list_len):
            for j in range(i+1,list_len):
                # compute distance between points
                a=list[i]
                b=list[j]
                # if object isn't active don't consider it for a collision
                if b.state != 'dead':
                    if are_two_points_in_range(a.x,a.y,b.x,b.y,a.radius+b.radius) == True:
                        # we have a collision, mark both parties
                        print("Collision Detected")
                        a.state=b.state='dead'
                    else:
                        # mark the object active after a move
                        if a.state=='init':
                           a.state='active'
                        if b.state=='init':
                            b.state='active'


# Create global list of objects in the world -- REST API instances will reference this
GLOBAL_OBJECT_LIST=world_object_list("init-world.json")



# Classes, functions and variables for implementing the REST API
obj_parser = reqparse.RequestParser()
obj_parser.add_argument('id', type=str,help='each object has a unique ID')
obj_parser.add_argument('name', type=str,help='each object must have a unique name')
obj_parser.add_argument('type',type=str,help='Type of object (target,attacker,defender,obstacle)')
obj_parser.add_argument('x',type=int,help='X coordinate of object')
obj_parser.add_argument('y',type=int,help='Y coordinate of object')
obj_parser.add_argument('radius',type=int,help='Radius of object in meters')
obj_parser.add_argument('state',type=str,help='State of of object (init,active,dead')
obj_parser.add_argument('scanrange',type=int,help='Range of scan to perform in meters')

resource_fields = {
    'id':    fields.String,
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

class all_objects_by_type(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list=GLOBAL_OBJECT_LIST

    def get(self,type):
        list=self.list.get_list()
        result=[]
        for each in list:
            if each['type'] == type:
                result.append(each)
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




class object_by_id(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list=GLOBAL_OBJECT_LIST

    def abort_if_id_exists(self,id):
        for each in self.list.object_list:
            if each.id == id:
                abort(409,message="id {} already exists".format(id))

    def abort_if_id_doesnt_exist(self,id):
        for each in self.list.object_list:
            if each.id == id:
                return each
        # if you made it here, there was no match
        abort(404,message="id {} doesn't exist".format(id))

    def get(self, obj_id):
        list=self.list.object_list
        match=self.abort_if_id_doesnt_exist(obj_id)
        return (match.serialize())
        
    def delete(self,obj_id):
        match = self.abort_if_id_doesnt_exist(obj_id)
        self.list.object_list.remove(match)
        return "",202


class object_by_name(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list=GLOBAL_OBJECT_LIST

    def abort_if_name_exists(self,name):
        for each in self.list.object_list:
            if each.name == name:
                abort(409,message="name {} already exists".format(name))

    def abort_if_name_doesnt_exist(self,name):
        for each in self.list.object_list:
            if each.name == name:
                return each
        # if you made it here, there was no match
        abort(404,message="name {} doesn't exist".format(name))


    def get(self, name):
        for each in self.list.object_list:
            if each.name == name:
                return (each.serialize())
        # if we made it here, no id match was found
        abort(404,message="name {} not found".format(name))

    # use the post method to create a new object
    def post(self, name):
        args = obj_parser.parse_args()
        self.abort_if_name_exists(name)
                
        # name doesn't exist, create object and append to the list
        new_obj = world_object(name,args['type'],args['x'],args['y'],args['radius'],args['state'],None)
        self.list.object_list.append(new_obj)
        return new_obj.serialize(), 200

    # use the put method to update an existing object. You can update x,y,radius and state
    def put(self,name):
        args = obj_parser.parse_args()
        # find named object
        match=self.abort_if_name_doesnt_exist(name)
        match.x = args['x'] if args['x'] is not None else match.x 
        match.y = args['y'] if args['y'] is not None else match.y
        match.radius = args['radius'] if args['radius'] is not None else match.radius  
        match.state = args['state'] if args['state'] is not None else match.state 

        # check for collisions since we might've changed position or radius
        self.list.update_collisions()
        return match.serialize()

    def delete(self,name):
        match = self.abort_if_name_doesnt_exist(name)
        self.list.object_list.remove(match)
        return "",202  


class sensor_by_name(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.list=GLOBAL_OBJECT_LIST

    def abort_if_id_doesnt_exist(self,name):
        for each in self.list.object_list:
            if each.name == name:
                return each
        # if you made it here, there was no match
        abort(404,message="name {} doesn't exist".format(name))

    def get(self,name):
        scan=[]
        args = obj_parser.parse_args()
        # get the world_object with the right name
        match=self.abort_if_id_doesnt_exist(name)
        list=self.object_list
        list_len=len(self.object_list)
        for i in range(0,list_len):
            a=list[i]
            b=match
            # don't match yourself
            if a.name != b.name:
                if are_two_points_in_range(a.x,a.y,b.x,b.y,args['scanrange']) == True:
                    scan.append(a)                
        return scan,200
        


if __name__ == "__main__":
    # add api endpoints
    api.add_resource(all_objects, '/v1/objects/')       # returns json list of all objects in the world
    api.add_resource(all_objects_by_type, '/v1/objects/types/<type>')     # get a list of objects based on type
    api.add_resource(object_by_index, '/v1/objects/index/<int:obj_index>')  # get a single object based on list index
    api.add_resource(object_by_id, '/v1/objects/id/<obj_id>') # get a single object based on id
    api.add_resource(object_by_name, '/v1/objects/name/<name>') # get/post/put/delete a single object based on name
    api.add_resource(sensor_by_name, '/v1/sensors/name/<name>') # get a sensor reading from a named object


    app.run(debug=True)

    
    

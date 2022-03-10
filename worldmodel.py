from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

# based on example from https://medium.com/duomly-blockchain-online-courses/how-to-create-a-simple-rest-api-with-python-and-flask-in-5-minutes-94bb88f74a23

# initial list of world model objects
WMObjects = {
    '1': {'uuid': '0001', 'type': 'attacker', 'x': 10, 'y': 10},
    '2': {'uuid': '0001', 'type': 'attacker', 'x': 10, 'y': 20},
    '3': {'uuid': '0002', 'type': 'defender', 'x': 20, 'y': 10},
    '4': {'uuid': '0003', 'type': 'defender', 'x': 30, 'y': 10},
    '5': {'uuid': '0004', 'type': 'target', 'x': 40, 'y': 10},
    '6': {'uuid': '0005', 'type': 'obstacle', 'x': 20, 'y': 20},
}

parser = reqparse.RequestParser()

class WMObjectsList(Resource):
    def get(self):
        return WMObjects

    def post(self):

        parser.add_argument("uuid")
        parser.add_argument("type")
        parser.add_argument("x")
        parser.add_argument("y")
        args = parser.parse_args()
        wmobject_id = int(max(WMObjects.keys())) + 1
        wmobject_id = '%i' % wmobject_id
        WMObjects[wmobject_id] = {
            "uuid": args["uuid"],
            "type": args["type"],
            "x": args["x"],
            "y": args["y"],
        }
        return WMObjects[wmobject_id], 201

class WMObject(Resource):
  def get(self, wmobject_id):
    if wmobject_id not in WMObjects:
        return "Not found", 404
    else:
        return WMObjects[wmobject_id]

  def put(self, wmobject_id):
    parser.add_argument("uuid")
    parser.add_argument("type")
    parser.add_argument("x")
    parser.add_argument("y")
    args = parser.parse_args()
    if wmobject_id not in WMObjects:
        return "Record not found", 404
    else:
        wmobject = WMObjects[wmobject_id]
        wmobject["uuid"] = args["uuid"] if args["uuid"] is not None else wmobject["uuid"]
        wmobject["type"] = args["type"] if args["type"] is not None else wmobject["type"]
        wmobject["x"] = args["x"] if args["x"] is not None else wmobject["x"]
        wmobject["y"] = args["y"] if args["y"] is not None else wmobject["y"]
        return wmobject, 200

  def delete(self, wmobject_id):
    if wmobject_id not in WMObjects:
        return "Not found", 404
    else:
        del WMObjects[wmobject_id]
        return '', 204


class WMAttackerList(Resource):
    def get(self):
        return "Attacker List not implemented yet"
    
class WMDefenderList(Resource):
    def get(self):
        return "Defender List not implemented yet"

class WMTargetList(Resource):
    def get(self):
        return "Target List not implemented yet"

class WMObstacleList(Resource):
    def get(self):
        return "Obstacle List not implemented yet"


if __name__ == "__main__":
    api.add_resource(WMObjectsList, '/objects/')
    api.add_resource(WMObject, '/objects/<wmobject_id>')
    api.add_resource(WMAttackerList, '/attackers/')
    api.add_resource(WMDefenderList, '/defenders/')
    api.add_resource(WMTargetList, '/targets/')
    api.add_resource(WMObstacleList, '/obstacles/')
    app.run(debug=True)
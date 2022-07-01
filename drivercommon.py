"""
Common classes used by driver programs
"""
import math as m
from tkinter import N
from dataclasses import dataclass
import numpy as np
import euclid as eu
import requests as req
import json
import time
import sys


# set some constants
DEFAULT_DELTA_T = 0.1  # main loop period
DEFAULT_HITBOX_MARGIN = 12.0
DEFAULT_SCANRANGE = 50
DEFAULT_RETRY_PERIOD = 10
DEFAULT_SERVER_ADDRESS = "http://localhost:5000"


# define point class that includes rotation value
class Point(eu.Point2):
    """Class to extend euclid Point2 class with rotation"""

    def __init__(self, x: float, y: float, rotation: float = 0.0) -> None:
        super().__init__(x, y)
        self.rotation = rotation

    # return distance between this point and x,y passed in
    def dist(self, x: float, y: float) -> float:
        dx = self.x - x
        dy = self.y - y
        a = self.distance()
        return m.hypot(dx, dy)

    # convert Point's cartesian x,y to polar rho,phi
    def car2pol(self) -> tuple:
        # phi returned in degrees
        rho = m.hypot(self.x, self.y)
        phi = np.arctan2(self.y, self.x)
        return (rho, np.rad2deg(phi))

    def pol2car(self, rho, phi) -> tuple:
        # phi passed in as degrees
        x = rho * np.cos(np.deg2rad(phi))
        y = rho * np.sin(np.deg2rad(phi))
        return (x, y)


class Object(Point):
    """Class to hold all parameters associated with object in World Model server"""

    def __init__(
        self,
        x: float,
        y: float,
        rotation: float,
        radius: float,
        speed: float,
        type: str,
        name: str,
        state: str,
        id: str = None,
    ) -> None:
        super().__init__(x, y, rotation)
        self.id = id
        self.name = name
        self.type = type
        self.radius = radius
        self.speed = speed
        self.state = state

    def get_point(self) -> Point:
        """Return a Point object with same x,y,rotation"""
        return Point(self.x, self.y, self.rotation)

    def set_point(self, p: Point) -> None:
        """Update Point variables, x,y,rotation in the Object."""
        """     - Does not send update to World Model REST server"""
        self.x = p.x
        self.y = p.y
        self.rotation = p.rotation

    # return circle representing object's radius and current position
    def hitbox(self, margin) -> eu.Circle:
        return eu.Circle(eu.Point2(self.x, self.y), self.radius + margin)

    # if an object is a target, we want to hit it
    def is_target(self) -> bool:
        if self.type == "target":
            return True
        else:
            return False

    def jsonify(self) -> dict:
        json_data = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "rotation": self.rotation,
            "speed": self.speed,
            "state": self.state,
        }
        return json_data


class PathVars:
    """Class to keep track of path-related values derived from speed, line segment, etc"""

    def __init__(
        self,
        delta_t: float,
        speed: float,
        evasive_path_angle: float = 0.0,
    ) -> None:

        self.delta_t: float = delta_t  # length of tick in seconds
        self.speed: float = speed  # speed of object
        self.delta_hypot: float = delta_t * speed  # distance along line per tick
        self.evasive_path_angle: float = (
            evasive_path_angle  # default delta angle to use when avoiding obstacle
        )
        self.s: float = 0.0  # time or parametric independent variable

    def increment_tick(self) -> None:
        self.s += self.delta_t


# PathSegment goes between 2 points.
class PathSegment:
    """Class to create a path between 2 Points"""

    def __init__(self, obj: Object, goal: Point) -> None:
        self.p1 = obj  # object starting point
        self.p2 = goal  # ending point
        self.line = eu.Line2(obj.get_point(), goal)
        self.my_radius = obj.radius
        self.delta_x = goal.x - obj.x
        self.delta_y = goal.y - obj.y
        self.delta_rotation = goal.rotation - obj.rotation
        # detect vertical line, which can't use y=mx+b
        if obj.x == goal.x:
            # vertical is a special case that has no slope
            self.type = "vertical"
            self.slope = None
            self.x = self.p1.x
            self.length = abs(self.delta_y)
        else:
            self.type = "nonvertical"
            # solve for slope and y intercept
            self.slope = self.delta_y / self.delta_x
            self.y_intercept = self.p1.y - (self.slope * self.p1.x)
            self.length = m.hypot(self.delta_x, self.delta_y)

            # compute theta, the angle of the line in radians, for future use
            self.theta = m.acos((self.delta_x) / self.length)

    # check path ahead and return true if we're on collision course
    # up to caller to check whether object is a target or not
    def might_collide(self, obstacle: Object) -> bool:
        obstacle_hitbox = obstacle.hitbox(margin=DEFAULT_HITBOX_MARGIN)
        dist = self.line.distance(obstacle_hitbox)
        if self.line.intersect(obstacle_hitbox):
            return True

        if self.my_radius + obstacle_hitbox.r < dist:
            return True

        return False

    def is_segment_complete(self, p: Point) -> bool:
        if m.hypot(p.x - self.p1.x, p.y - self.p1.y) >= self.length:
            return True
        else:
            return False

    def distance_per_tick(self, delta_t: float, speed: float) -> float:
        """compute distance per tick based on speed and update rate"""
        return delta_t * speed

    # compute point that is s percent alont the segment
    # s=0.0 returns p1, s=100.0 returns p2
    def compute_parametric_point(self, s: float) -> Point:
        p = Point(0, 0, 0)
        s = s / 100.0
        if self.type == "vertical":
            p.x = self.x
            p.y = self.pt.y + (s * self.delta_y)
        else:
            # nonvertical, compute y=mx+b
            p.x = self.p1.x + (s * self.delta_x)
            p.y = self.slope * p.x + self.y_intercept
        # compute new object rotation
        p.rotation = self.pt.rotation + (s * self.deta_rotation)
        self.last_pos = p
        return self.last_pos

    def compute_delta_point(self, cur_point: Point, path_vars: PathVars) -> Point:
        """compute next point based on current point and delta distance along line"""
        if path_vars.delta_hypot == 0.0:
            return cur_point

        p = Point(0.0, 0.0, cur_point.rotation)
        # p.rotation = cur_point.rotation + path_vars.delta_rotation
        if self.type == "vertical":
            p.x = cur_point.x
            p.y += path_vars.delta_hypot
            return p
        else:
            # compute delta x, given delta distance along hypotenuse and theta
            dx = path_vars.delta_hypot * m.cos(self.theta)

            # now add delta x to previous x and compute y
            p.x = cur_point.x + dx
            p.y = self.slope * p.x + self.y_intercept
            return p


class DriverRestClient:
    """Client that interacts with the World Model REST API."""

    def __init__(self, server_address) -> None:
        self.OBJECT_BY_NAME_API_PATH = "/v1/objects/name/"
        self.OBJECTS_ALL_API_PATH = "/v1/objects/"
        self.SENSOR_API_PATH = "/v1/sensors/name/"
        self.object_by_name_url = server_address + self.OBJECT_BY_NAME_API_PATH
        self.objects_all_url = server_address + self.OBJECTS_ALL_API_PATH
        self.sensors_url = server_address + self.SENSOR_API_PATH
        return

    # create a new object on the Rest Server
    def create_new_object(self, new_obj):
        """Create a new object on the World Model REST server"""
        url = self.object_by_name_url + new_obj.name
        json_data = new_obj.jsonify()
        try:
            r = req.post(url, data=json_data)
            return r
        except req.exceptions.req.RequestException:
            print(f"failed to connect to server {self.object_by_name_url}")
            print(f"")

    def delete_named_object(self, obj_name):
        """Delete an object from the World Model REST server"""
        url = self.object_by_name_url + obj_name
        try:
            r = req.delete(url)
            return r
        except req.exceptions.req.RequestException:
            print(f"failed to connect to server {self.object_by_name_url}")
            print(f"")

    # new functions, trying to make DriverRestClient more logical
    def get_named_object(self, name: str) -> Object:
        """Return an Object containing the state of the named object"""
        try:
            rsp = req.get(self.object_by_name_url + name)
            obj_state = json.loads(rsp.text)
            if obj_state is not None:
                return Object(
                    float(obj_state["x"]),
                    float(obj_state["y"]),
                    float(obj_state["rotation"]),
                    float(obj_state["radius"]),
                    float(obj_state["speed"]),
                    obj_state["type"],
                    obj_state["name"],
                    obj_state["state"],
                    obj_state["id"],
                )
            else:
                return None
        except req.exceptions.RequestException:
            print(f"failed to connect to server {self.object_by_name_url}")
            return None

    def set_named_object(self, obj: Object):
        url = self.object_by_name_url + obj.name
        json_data = obj.jsonify()
        try:
            r = req.put(url, data=json_data)
            return r
        except req.exceptions.req.RequestException:
            print(f"failed to connect to server {self.object_by_name_url}")
            print(f"")

    def get_named_object_json(self, name: str) -> list:
        """Return an json list containing the state of the named object"""
        try:
            rsp = req.get(self.object_by_name_url + name)
            return json.loads(rsp.text)
        except req.exceptions.RequestException:
            print(f"failed to connect to server {self.object_by_name_url}")
            return None

    def get_all_objects(self) -> list:
        """Return all objects in the world model as a list of Objects"""
        url = self.objects_all_url
        try:
            rsp = req.get(url)
            obj_list = json.loads(rsp.text)
            return_list = []
            for each in obj_list:
                return_list.append(
                    Object(
                        float(each["x"]),
                        float(each["y"]),
                        float(each["rotation"]),
                        float(each["radius"]),
                        float(each["speed"]),
                        each["type"],
                        each["name"],
                        each["state"],
                        each["id"],
                    )
                )
            return return_list
        except req.exceptions.RequestException:
            print(f"failed to connect to server {self.object_by_name_url}")
            return None

    def get_all_objects_json(self) -> list:
        """Return all objects in the world model as a json list"""
        try:
            rsp = req.get(self.objects_all_url)
            return json.loads(rsp.text)
        except req.exceptions.RequestException:
            print(f"failed to connect to server {self.object_by_name_url}")
            return None
        pass

    def get_sensors(self, name: str, scan_range: float) -> list:
        """Return a list of obstacle Objects with a radius of named object"""
        url = self.sensors_url + name + "?scanrange=" + str(scan_range)
        try:
            rsp = req.get(url)
            scan = json.loads(rsp.text)
            object_list = []
            # Convert string-based object into an Object with euclidean properties
            for each in scan:
                object_list.append(
                    Object(
                        x=float(each["x"]),
                        y=float(each["y"]),
                        rotation=float(each["rotation"]),
                        radius=float(each["radius"]),
                        speed=float(each["speed"]),
                        type=each["type"],
                        name=each["name"],
                        state=each["state"],
                        id=each["id"],
                    )
                )
            return object_list
        except req.exceptions.RequestException:
            print(f"failed to connect to server {self.object_by_name_url}")
            return None

    def get_sensors_json(self, name: str, scan_range: float) -> list:
        """Return a json list of obstacles within a radius of named object"""
        url = self.sensors_url + name + "?scanrange=" + str(scan_range)
        try:
            rsp = req.get(url)
            scan = json.loads(rsp.text)
            return scan
        except req.exceptions.RequestException:
            print(f"failed to connect to server {self.object_by_name_url}")
            return None

    def get_target(self) -> Object:
        """Return the object identified as the target"""
        list = self.get_all_objects()
        for each in list:
            if each.type == "target":
                return each

    def get_speed(self, name) -> float:
        """Get speed of named object"""
        o = self.get_named_object(name)
        return o.speed

    def set_speed(self, name, speed: float) -> None:
        """Set speed of named object"""
        o = self.get_named_object(name)
        o.speed = speed
        self.set_named_object(o)

    def wait_for_server(self, poll_period=DEFAULT_RETRY_PERIOD) -> None:
        """Wait forever for the server to connect"""
        list = self.get_all_objects_json()
        while list is None:
            time.sleep(poll_period)
            state = self.get_all_objects_json()

    def exit_if_dead(self, name: str):
        """Exit if the server has changed the object state to dead"""
        state = self.get_named_object(name)
        if state.state == "dead":
            sys.exit({"status": "Object is Dead"})
        else:
            return None


def rotate_segment(cur_pt: Point, nxt_pt: Point, angle_deg: float) -> Point:
    """rotate a line segment about its p1 through an angle in degrees"""
    dx = nxt_pt.x - cur_pt.x
    dy = nxt_pt.y - cur_pt.y
    dr = nxt_pt.rotation - cur_pt.rotation
    delta_pt = Point(dx, dy, dr)
    rho, phi = delta_pt.car2pol()
    phi += angle_deg
    new_x, new_y = delta_pt.pol2car(rho, phi)
    # add the current point back in
    new_x += cur_pt.x
    new_y += cur_pt.y
    new_r = nxt_pt.rotation
    new_point = Point(new_x, new_y, new_r)
    return new_point


def read_config_from_file(filename: str = "config/object.json") -> Object:
    """Read a config file and return contents as an Object"""
    with open(filename) as file:
        obj_state = json.load(file)
        return Object(
            float(obj_state["x"]),
            float(obj_state["y"]),
            float(obj_state["rotation"]),
            float(obj_state["radius"]),
            float(obj_state["speed"]),
            obj_state["type"],
            obj_state["name"],
            obj_state["state"],
            obj_state["id"],
        )


def instantiate_object_in_world(wmclient: DriverRestClient, config_filename) -> Object:
    """Read config file and instantiate new object on world server"""
    # read config file and instatiate object in the world server
    obj = read_config_from_file(config_filename)

    success = False
    while success == False:
        r = wmclient.create_new_object(obj)
        if r.status_code == 200:
            success = True
            print(f"Created {obj.name} from {config_filename} in REST server")
        elif r.status_code == 409:
            print(f"{obj.name} already exists, trying to delete")
            r = wmclient.delete_named_object(obj.name)
        else:
            print(f"unknown error trying to create {obj.name}")

    return obj

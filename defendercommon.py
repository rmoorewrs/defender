"""
Common classes used by defender programs
"""
import math as m
import numpy as np
import euclid as eu
import requests as req
import json
import time
import sys
import server_ip_multicast

# set some constants
DEFAULT_MAX_SPEED = 20  # maximum speed we can move
DEFAULT_DELTA_T = 0.1  # main loop period
DEFAULT_SCANRANGE = 50
DEFAULT_RETRY_PERIOD = 10
DEFAULT_SERVER_ADDRESS = "http://localhost:5000"
OBJECT_API_PATH = "/v1/objects/name/"
SENSOR_API_PATH = "/v1/sensors/name/"


# define point class that includes rotation value
class Point(eu.Point2):
    def __init__(self, x: float, y: float, rotation: float = 0.0) -> None:
        super().__init__(x, y)
        self.rotation_angle = rotation

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


# class that holds object parameters
class Object(Point):
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
        self.x = x
        self.y = y
        self.radius = radius
        self.rotation = rotation
        self.speed = speed
        self.state = state

    # return circle representing object's radius and current position
    def hitbox(self) -> eu.Circle:
        return eu.Circle(eu.Point2(self.x, self.y), self.radius)

    # if an object is a target, we want to hit it
    def is_target(self) -> bool:
        if self.type == "target":
            return True
        else:
            return False


# PathSegment goes between 2 points.
class PathSegment(eu.Line2):
    def __init__(
        self,
        pt1: Point,
        pt2: Point,
        my_radius: float,
        period: float = DEFAULT_DELTA_T,
        speed: float = DEFAULT_MAX_SPEED,
    ) -> None:
        super().__init__(pt1, pt2)
        self.last_pos = pt1
        self.pt1 = pt1  # starting point
        self.pt2 = pt2  # ending point
        self.my_radius = my_radius
        self.delta_x = pt2.x - pt1.x
        self.delta_y = pt2.y - pt1.y
        self.deta_rotation = pt2.rotation_angle - pt1.rotation_angle
        self.length = self.v.magnitude()
        # detect vertical line, which can't use y=mx+b
        if pt1.x == pt2.x:
            # vertical is a special case that has no slope
            self.type = "vertical"
            self.slope = None
            self.x = pt1.x
            self.length = abs(self.delta_y)
        else:
            self.type = "nonvertical"
            # solve for slope and y intercept
            self.slope = self.delta_y / self.delta_x
            self.y_intercept = pt1.y - (self.slope * pt1.x)
            self.length = m.hypot(self.delta_x, self.delta_y)

    # check path ahead and return true if we're on collision course
    # up to caller to check whether object is a target or not
    def might_collide(self, obstacle: Object) -> bool:
        hitbox = obstacle.hitbox()
        dist = self.distance(hitbox)
        if self.intersect(hitbox) or dist < self.my_radius + hitbox.r:
            return True
        else:
            return False

    def is_segment_complete(self, p: Point) -> bool:
        if (
            p.x == self.pt2.x
            and p.y == self.pt2.y
            and p.rotation == self.pt2.rotation_angle
        ):
            return True
        else:
            return False

    # compute point that is s percent alont the segment
    # s=0.0 returns p1, s=100.0 returns p2
    def compute_point(self, s: float) -> Point:
        p = Point(0, 0, 0)
        s = s / 100.0
        if self.type == "vertical":
            p.x = self.x
            p.y = self.pt1.y + (s * self.delta_y)
        else:
            # nonvertical, compute y=mx+b
            p.x = self.pt1.x + (s * self.delta_x)
            p.y = self.slope * p.x + self.y_intercept
        # compute new object rotation
        p.rotation = self.pt1.rotation_angle + (s * self.deta_rotation)
        self.last_pos = p
        return self.last_pos


# An object is something returned from world_model server which has a unique name
class DriverRestClient:
    def __init__(self, server_address, object_name) -> None:
        self.object_state_json = None
        self.sensor_scan = None
        self.object_state_url = server_address + OBJECT_API_PATH + object_name
        self.sensor_state_url = server_address + SENSOR_API_PATH + object_name
        return

    def get_object_state(self, json_format: bool = False) -> any:
        try:
            rsp = req.get(self.object_state_url)
            self.object_state_json = json.loads(rsp.text)
            if json_format is False:
                return Object(
                    float(self.object_state_json["x"]),
                    float(self.object_state_json["y"]),
                    float(self.object_state_json["rotation"]),
                    float(self.object_state_json["radius"]),
                    float(self.object_state_json["speed"]),
                    self.object_state_json["type"],
                    self.object_state_json["name"],
                    self.object_state_json["state"],
                    self.object_state_json["id"],
                )
            else:
                return self.object_state_json
        except req.exceptions.RequestException:
            print(f"failed to connect to server {self.object_state_url}")
            return None

    def set_object_state(self, json_state):
        self.object_state_json = json_state
        try:
            req.put(self.object_state_url, data=self.object_state_json)
        except req.exceptions.req.RequestException:
            print(f"failed to connect to server {self.object_state_url}")
            print(f"")

    # get object speed
    def get_speed(self) -> float:
        return float(self.object_state_json["speed"])

    # set object speed and write it out to the world_model server
    def set_speed(self, speed=DEFAULT_MAX_SPEED) -> dict:
        self.object_state_json["speed"] = speed
        self.set_object_state(self.object_state_json)
        return self.object_state_json

    def get_sensor_state(self, scan_range) -> list:
        try:
            rsp = req.get(self.sensor_state_url + "?scanrange=" + str(scan_range))
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
            print(f"failed to connect to server {self.object_state_url}")
            return None

    def wait_for_server(self, poll_period=DEFAULT_RETRY_PERIOD) -> dict:
        state = self.get_object_state()
        if state:
            return state
        else:
            while state is None:
                time.sleep(poll_period)
                state = self.get_object_state()

    def exit_if_dead(self):
        if self.object_state_json["state"] == "dead":
            sys.exit({"status": "Object is Dead"})
        else:
            return None

    def exit_if_outofbounds(self):
        pass

    def get_object(self) -> Object:
        return Object(self.x, self.y, self.rotation, self.radius, self.type)

    # get/set points
    def get_point(self) -> Point:
        p = Point(
            float(self.object_state_json["x"]),
            float(self.object_state_json["y"]),
            float(self.object_state_json["rotation"]),
        )
        return p

    def set_point(self, p: Point) -> None:
        new_state = self.get_object_state(json_format=True)
        new_state["x"] = p.x
        new_state["y"] = p.y
        new_state["rotation"] = p.rotation_angle
        self.set_object_state(new_state)

    def get_object(self) -> Object:
        return Object(
            x=float(self.object_state_json["x"]),
            y=float(self.object_state_json["y"]),
            rotation=float(self.object_state_json["rotation"]),
            radius=float(self.object_state_json["radius"]),
            speed=float(self.object_state_json["speed"]),
            type=self.object_state_json["type"],
            name=self.object_state_json["name"],
            state=self.object_state_json["state"],
            id=self.object_state_json["id"],
        )

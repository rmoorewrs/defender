"""
Common classes used by defender programs
"""
from math import exp, sqrt
import requests as req
import json
import time
import math
import sys
import server_ip_multicast

# set some constants
DEFAULT_MAX_SPEED = 10  # maximum speed we can move
DEFAULT_DELTA_T = 0.25  # main loop period
DEFAULT_SCANRANGE = 200
DEFAULT_RETRY_PERIOD = 10
DEFAULT_SERVER_ADDRESS = "http://localhost:5000"
OBJECT_API_PATH = "/v1/objects/name/"
SENSOR_API_PATH = "/v1/sensors/name/"


class Point:
    def __init__(self, x: float, y: float, rotation: float) -> None:
        self.x = x
        self.y = y
        self.rotation = rotation
        return None

    # return distance between this point and x,y passed in
    def distance(self, x: float, y: float) -> float:
        dx = self.x - x
        dy = self.y - y
        return sqrt(dx * dx + dy * dy)


# Base class for travel segments. All segments go between 2 points.
class Segment:
    def __init__(
        self,
        p1: Point,
        p2: Point,
        tick_period: float = DEFAULT_DELTA_T,
        speed: float = DEFAULT_MAX_SPEED,
    ) -> None:
        self.segment_finished = False
        self.p1 = p1
        self.p2 = p2
        self.delta_x = p2.x - p1.x
        self.delta_y = p2.y - p1.y
        self.deta_rotation = p2.rotation - p1.rotation
        self.speed = speed
        self.tick_period = tick_period
        self.tick_count = 0  # keep track of ticks advanced

        # set length traveled for each tick and compute number of ticks
        self.tick_travel = self.speed * self.tick_period
        self.n = self.length / self.tick_travel

    # functions that should be implemented by derived classes
    def compute_nth_point(self, count: float) -> Point:
        pass

    def advance_one_tick(self):
        pass


# Create a linear segment that gets from point 1 to point 2
class SegmentLinear(Segment):
    def __init__(
        self,
        p1: Point,
        p2: Point,
        tick_period: float = DEFAULT_DELTA_T,
        speed: float = DEFAULT_MAX_SPEED,
    ) -> None:
        super().__init__(p1, p2, tick_period, speed)

        # detect vertical line, which can't use y=mx+b
        if p1.x == p2.x:
            # vertical is a special case that has no slope
            self.type = "vertical"
            self.slope = None
            self.x = p1.x
            self.length = abs(self.delta_y)
        else:
            self.type = "nonvertical"
            # solve for slope and y intercept
            self.slope = self.delta_y / self.delta_x
            self.y_intercept = p1.y - (self.slope * p1.x)
            self.length = sqrt(
                self.delta_x * self.delta_x + self.delta_y * self.delta_y
            )
        # set length traveled for each tick and compute number of ticks
        self.tick_travel = self.speed * self.tick_period
        self.n = self.length / self.tick_travel

    def compute_nth_point(self, count: float) -> Point:
        p = Point(0, 0, 0)
        percent_traveled = count / self.n
        if self.type == "vertical":
            p.x = self.x
            p.y = self.p1.y + (percent_traveled * self.delta_y)
        else:
            # nonvertical, compute y=mx+b
            p.x = self.p1.x + (percent_traveled * self.delta_x)
            p.y = self.slope * p.x + self.y_intercept
        # compute new rotation
        p.rotation = self.p1.rotation + (percent_traveled * self.deta_rotation)
        return p

    # advance forward by one tick's worth, return True if finished
    def advance_one_tick(self):
        self.tick_count += 1
        p = self.compute_nth_point(self.tick_count)
        # check to see if we're on the last chunk, return the goal if so
        if p.distance(self.p2.x, self.p2.y) < self.tick_travel:
            self.segment_finished = True
            p = self.p2
        return p, self.segment_finished


# class for handling object state operations
class ObjectState:
    def __init__(self, server_address, object_name) -> None:
        self.object_state = None
        self.sensor_scan = None
        self.object_state_url = server_address + OBJECT_API_PATH + object_name
        self.sensor_state_url = server_address + SENSOR_API_PATH + object_name
        return

    def get_object_state(self) -> dict:
        try:
            rsp = req.get(self.object_state_url)
            self.object_state = json.loads(rsp.text)
            return self.object_state
        except req.exceptions.RequestException:
            print(f"failed to connect to server {self.object_state_url}")
            return None

    def set_state(self, state):
        self.object_state = state
        try:
            req.put(self.object_state_url, data=self.object_state)
        except req.exceptions.req.RequestException:
            print(f"failed to connect to server {self.object_state_url}")
            print(f"")

    # set speed and write it out to the REST server
    def set_speed(self, speed=DEFAULT_MAX_SPEED) -> dict:
        self.object_state["speed"] = speed
        self.set_state(self.object_state)
        return self.object_state

    def get_sensor_state(self, scan_range) -> dict:
        try:
            rsp = req.get(self.sensor_state_url + "?scanrange=" + str(scan_range))
            sensor_scan = json.loads(rsp.text)
            return sensor_scan
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

    def abort_if_dead(self):
        if self.object_state["state"] == "dead":
            sys.exit({"status": "Object is Dead"})
        else:
            return None

    def abort_if_outofbounds(self):
        pass

    def get_point(self) -> Point:
        p = Point(
            self.object_state["x"],
            self.object_state["y"],
            self.object_state["rotation"],
        )
        return p

    def set_point(self, p: Point) -> None:
        new_state = self.get_object_state
        new_state["x"] = p.x
        new_state["y"] = p.y
        new_state["rotation"] = p.rotation
        self.set_state(new_state)

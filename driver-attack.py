from defendercommon import (
    Point,
    SegmentLinear,
    ObjectState,
    DEFAULT_SERVER_ADDRESS,
    DEFAULT_SCANRANGE,
    DEFAULT_MAX_SPEED,
    DEFAULT_RETRY_PERIOD,
    DEFAULT_DELTA_T,
)
from flask_restful import abort
import requests as req
import json
import time
import math
import sys
import server_ip_multicast

# set some parameters
# MAX_SPEED = 10  # maximum speed we can move
# DELTA_T = 0.25  # main loop period
RETRY_PERIOD = 10  # delay if we're not connecting to server
GOAL_POINT = {"x": 295, "y": 50, "rotation": 0}
OBJECT_STATE = None
SENSOR_STATE = None
OBJECT_STATE_URL = ""
SENSOR_STATE_URL = ""


class Path:
    def __init__(self, goal: Point, path_type="direct"):
        self.goal = goal


def sense_environment(state: ObjectState, scan_range):
    sensor_scan = state.get_sensor_state(scan_range)
    return sensor_scan


def usage_and_exit(app_name):
    print(f"{app_name} <object_name> [server IP:port | multicast]")
    print("<object_name> must be a valid object")
    sys.exit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage_and_exit(sys.argv[0])

    # get name of object to move around in world-model
    object_name = sys.argv[1]

    # check for IP or multicast
    server_address = DEFAULT_SERVER_ADDRESS  # set default worldserver address
    if len(sys.argv) == 3:
        if sys.argv[2] == "multicast":
            server_address = server_ip_multicast.wait_forever_for_server_address()
        else:
            server_address = "http://" + sys.argv[2]

    # get initial state, initial sensor readings and set object speed
    state = ObjectState(server_address, object_name)
    obj_url = state.object_state_url
    sensor_url = state.sensor_state_url
    print(
        f"{object_name} driver connecting to {server_address} using full API path {obj_url}"
    )
    print(
        f"{object_name} scanning from {server_address} using full API path {sensor_url}"
    )

    # Initialize - wait until server becomes available, set initial conditions
    state.wait_for_server()
    OBJECT_STATE = state.get_object_state()
    SENSOR_STATE = state.get_sensor_state(DEFAULT_SCANRANGE)
    OBJECT_STATE = state.set_speed(DEFAULT_MAX_SPEED)

    # Loop until dead - sense, plan, execute
    path_type = "direct"  # could be direct, curve, random

    # set up a straight segment that goes directly to the goal point
    current_point = Point(
        OBJECT_STATE["x"], OBJECT_STATE["y"], OBJECT_STATE["rotation"]
    )
    goal_point = Point(
        float(GOAL_POINT["x"]), float(GOAL_POINT["y"]), float(GOAL_POINT["rotation"])
    )
    path_seg = SegmentLinear(
        current_point, goal_point, DEFAULT_DELTA_T, DEFAULT_MAX_SPEED
    )
    # loop while object is still viable
    while True:
        obj_state = state.get_object_state()
        if obj_state:
            # sensor_scan = sense_environment(state, DEFAULT_SCANRANGE)
            # path = plan_path(path_type)
            p_next, segment_done = path_seg.advance_one_tick()
            state.set_point(p_next)

            # execute_plan(path)
            state.abort_if_outofbounds()
            state.abort_if_dead()

        time.sleep(DEFAULT_DELTA_T)

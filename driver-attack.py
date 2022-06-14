from glob import glob
import defendercommon as dc
import euclid as eu
import numpy as np
import requests as req
import json
import time
import math as m
import sys
import server_ip_multicast

# set some parameters
# MAX_SPEED = 10  # maximum speed we can move
# DELTA_T = 0.25  # main loop period
RETRY_PERIOD = 10  # delay if we're not connecting to server
GOAL_POINT = dc.Point(295.0, 50.0, 0.0)
OBJECT_STATE = None
SENSOR_STATE = None
OBJECT_STATE_URL = ""
SENSOR_STATE_URL = ""
PATH_TO_GOAL: dc.PathSegment = None
MY_RADIUS: float = 0.0
S = 0.0  # parametric path independent variable, 0 <= s <= 100.0

# rotate a line segment about its p1 through an angle in degrees
def rotate_segment(cur_pt: dc.Point, nxt_pt: dc.Point, angle_deg: float) -> dc.Point:
    dx = nxt_pt.x - cur_pt.x
    dy = nxt_pt.y - cur_pt.y
    dr = nxt_pt.rotation_angle - cur_pt.rotation_angle
    delta_pt = dc.Point(dx, dy, dr)
    rho, phi = delta_pt.car2pol()
    phi += angle_deg
    new_x, new_y = delta_pt.pol2car(rho, phi)
    # add the current point back in
    new_x += cur_pt.x
    new_y += cur_pt.y
    new_r = nxt_pt.rotation_angle
    new_point = dc.Point(new_x, new_y, new_r)
    return new_point


# return either the next point on pathsegment or evasive course
def plan_next_point(s: float, myself: dc.Object, sensor_scan: list):
    global PATH_TO_GOAL, S, MY_RADIUS

    corrective_angle = 10.0

    # check for potential collision
    current_point = dc.Point(myself.x, myself.y, myself.rotation)
    next_point = PATH_TO_GOAL.compute_point(s)
    for each in sensor_scan:
        # we want to collide with a target, but not any other object
        if each.is_target() is False and PATH_TO_GOAL.might_collide(each) is True:
            # try rotating segment point to avoid collision
            new_point = rotate_segment(current_point, next_point, corrective_angle)
            # now must compute new path to goalpoint/target
            PATH_TO_GOAL = dc.PathSegment(
                new_point,
                GOAL_POINT,
                MY_RADIUS,
                dc.DEFAULT_DELTA_T,
                dc.DEFAULT_MAX_SPEED,
            )
            # reset path parametric independent variable
            S = 0.0
            next_point = new_point
    return next_point


def usage_and_exit(app_name):
    print(f"{app_name} <object_name> [server IP:port | multicast]")
    print("<object_name> must be a valid object")
    sys.exit()


def main():
    global PATH_TO_GOAL, MY_RADIUS, S

    if len(sys.argv) < 2:
        usage_and_exit(sys.argv[0])

    # get name of object to move around in world-model
    object_name = sys.argv[1]

    # check for IP or multicast
    server_address = dc.DEFAULT_SERVER_ADDRESS  # set default worldserver address
    if len(sys.argv) == 3:
        if sys.argv[2] == "multicast":
            server_address = server_ip_multicast.wait_forever_for_server_address()
        else:
            server_address = "http://" + sys.argv[2]

    # get initial state, initial sensor readings and set object speed
    state = dc.DriverRestClient(server_address, object_name)
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
    OBJECT_STATE = state.get_object_state(json_format=True)
    SENSOR_STATE = state.get_sensor_state(100)
    OBJECT_STATE = state.set_speed(dc.DEFAULT_MAX_SPEED)
    MY_RADIUS = float(OBJECT_STATE["radius"])  # use for collision detection

    # create a path that goes directly to the goal point
    current_point = dc.Point(
        OBJECT_STATE["x"], OBJECT_STATE["y"], OBJECT_STATE["rotation"]
    )
    goal_point = GOAL_POINT
    PATH_TO_GOAL = dc.PathSegment(
        current_point,
        goal_point,
        MY_RADIUS,
        dc.DEFAULT_DELTA_T,
        dc.DEFAULT_MAX_SPEED,
    )

    # loop while object isn't dead or out of bounds
    while True:
        obj_state = state.get_object_state(json_format=True)
        obj = state.get_object()

        if obj_state:
            sensor_scan = state.get_sensor_state(dc.DEFAULT_SCANRANGE)
            S += dc.DEFAULT_DELTA_T
            next_point = plan_next_point(S, obj, sensor_scan)
            state.set_point(next_point)

            # execute_plan(path)
            state.exit_if_outofbounds()
            state.exit_if_dead()

        time.sleep(dc.DEFAULT_DELTA_T)


if __name__ == "__main__":
    main()

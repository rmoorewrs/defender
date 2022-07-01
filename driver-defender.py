import drivercommon as dc
import euclid as eu
import numpy as np
import requests as req
import json
import time
import math as m
import sys

RETRY_PERIOD = 10.0  # delay if we're not connecting to server
CLOCK_TICK = 0.03
EVASIVE_PATH_ANGLE = 30.0  # used when computing simple obstacle avoidance
RIGHT_LIMIT = 500.0
LEFT_LIMIT = 0.0
RIGHT_TRAVEL = 90.0
LEFT_TRAVEL = 270.0


def plan_next_point_simple(
    path: dc.PathSegment, path_vars: dc.PathVars, myself: dc.Object
):

    # check for potential collision
    current_point = dc.Point(myself.x, myself.y, myself.rotation)
    next_point = path.compute_delta_point(current_point, path_vars)
    return next_point


def set_goal_point(wmclient: dc.DriverRestClient) -> dc.Point:
    """Return a goal point that points to the target"""
    """ This should be set by some other means, but will do for now"""
    target = wmclient.get_target()
    return dc.Point(target.x, target.y, target.rotation)


def usage_and_exit(app_name):
    print(f"{app_name} <config_filename> server IP:port [simple | avoid]")
    print("- <config_filename> is the name of a json config file")
    print("- server address must be a string like 'localhost:5000'")
    sys.exit()


def main():

    #########################################################
    #  Initialization
    #########################################################
    if len(sys.argv) < 2:
        usage_and_exit(sys.argv[0])

    # get name of object config file and IP address
    config_filename = sys.argv[1]

    server_address = dc.DEFAULT_SERVER_ADDRESS  # set default worldserver address
    if len(sys.argv) >= 3:
        server_address = "http://" + sys.argv[2]

    # Create rest client (wmclient) to talk to world model server and wait until client connects
    wmclient = dc.DriverRestClient(server_address)
    wmclient.wait_for_server()

    obj = dc.instantiate_object_in_world(wmclient, config_filename)
    obj_name = obj.name

    # Get the sensor state of the object we're controlling (an attacker)
    # sensors = wmclient.get_sensors(obj_name, 100)  # the obstacles it can see

    # must move back and forth between 2 points along horizontal line
    left_goal = dc.Point(LEFT_LIMIT + 10.0, obj.y, LEFT_TRAVEL)
    right_goal = dc.Point(RIGHT_LIMIT - 10.0, obj.y, RIGHT_TRAVEL)

    # are we starting to the left or right?
    direction = RIGHT_TRAVEL
    if obj.x - LEFT_LIMIT < RIGHT_LIMIT - obj.x:
        direction = RIGHT_TRAVEL  # we're to the left
        path = dc.PathSegment(obj, right_goal)
    elif obj.x - LEFT_LIMIT > RIGHT_LIMIT - obj.x:
        direction = LEFT_TRAVEL  # we're to the right
        path = dc.PathSegment(obj, left_goal)

    # path_vars holds parameters for computing points in a path
    path_vars = dc.PathVars(CLOCK_TICK, obj.speed, 0)

    #########################################################
    #  Loop while our object is active
    #########################################################
    while True:
        # always start with current position/state from the wmclient
        obj = wmclient.get_named_object(obj_name)

        # PATH PLANNING
        if obj:
            path_vars.increment_tick()  # increment clock
            next_point = plan_next_point_simple(path, path_vars, obj)
            obj.set_point(next_point)  # update current object with next point

            # move to computed next point
            wmclient.set_named_object(obj)  # send updated object to world model server
            wmclient.exit_if_dead(obj_name)

        # check to see if we've reached goal
        if path.is_segment_complete(obj) is True:
            # are we at right or left goal?
            if obj.x >= right_goal.x:
                obj.rotation = LEFT_TRAVEL
                path = dc.PathSegment(obj, left_goal)
            else:
                path = dc.PathSegment(obj, right_goal)
                obj.rotation = RIGHT_TRAVEL
            wmclient.set_named_object(obj)

        time.sleep(CLOCK_TICK)


if __name__ == "__main__":
    main()

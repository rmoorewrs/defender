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


def plan_next_point_simple(
    path: dc.PathSegment, path_vars: dc.PathVars, myself: dc.Object
):

    # check for potential collision
    current_point = dc.Point(myself.x, myself.y, myself.rotation)
    next_point = path.compute_delta_point(current_point, path_vars)
    return next_point


# return either the next point on pathsegment or evasive course
def plan_next_point_with_avoidance(
    path: dc.PathSegment, path_vars: dc.PathVars, myself: dc.Object, sensor_scan: list
):

    # check for potential collision
    current_point = dc.Point(myself.x, myself.y, myself.rotation)
    goal_point = dc.Point(path.p2.x, path.p2.y, path.p2.rotation)
    next_point = path.compute_delta_point(current_point, path_vars)
    # if there are no obstacles in scan range, continue
    recompute_path = False
    if len(sensor_scan) > 0:
        for each in sensor_scan:
            # we want to collide with a target, but not any other object
            if each.type != "target" and path.might_collide(each) is True:
                # try rotating segment point to avoid collision
                next_point = dc.rotate_segment(
                    current_point, next_point, path_vars.evasive_path_angle
                )
                recompute_path = True
    return next_point, recompute_path


def set_goal_point(wmclient: dc.DriverRestClient) -> dc.Point:
    """Return a goal point that points to the target"""
    """ This should be set by some other means, but will do for now"""
    target = wmclient.get_target()
    return dc.Point(target.x, target.y, target.rotation)


def usage_and_exit(app_name):
    print(f"{app_name} <config_filename> server IP:port [simple | avoid]")
    print("- <config_filename> is the name of a json config file")
    print("- server address must be a string like 'localhost:5000'")
    print("- path planning must either be 'simple' or 'avoid'")
    sys.exit()


def main():

    #########################################################
    #  Initialization
    #########################################################
    if len(sys.argv) < 2:
        usage_and_exit(sys.argv[0])

    # get name of object to move around in world-model and IP address
    config_filename = sys.argv[1]

    server_address = dc.DEFAULT_SERVER_ADDRESS  # set default worldserver address
    if len(sys.argv) >= 3:
        server_address = "http://" + sys.argv[2]

    # set path planning method
    path_planning = "simple"
    if len(sys.argv) >= 4:
        if sys.argv[3] == "simple" or sys.argv[3] == "avoid":
            path_planning = sys.argv[3]
        else:
            usage_and_exit(sys.argv[0])
    print(f"Path Planning Strategy: {path_planning}")

    # Create rest client (wmclient) to talk to world model server and wait until client connects
    wmclient = dc.DriverRestClient(server_address)
    wmclient.wait_for_server()

    # read config file and instatiate object in the world server
    obj = dc.read_config_from_file(config_filename)
    obj_name = obj.name
    # named object may already exist. If so, delete and try again
    success = False
    while success == False:
        r = wmclient.create_new_object(obj)
        if r.status_code == 200:
            success = True
            print(f"Created {obj_name} from {config_filename} in REST server")
        elif r.status_code == 409:
            print(f"{obj_name} already exists, trying to delete")
            r = wmclient.delete_named_object(obj_name)
        else:
            print(f"unknown error trying to create {obj_name}")

    # Get the sensor state of the object we're controlling (an attacker)
    sensors = wmclient.get_sensors(obj_name, 100)  # the obstacles it can see

    # create a path segment between current point and goal point
    goal = set_goal_point(wmclient)  # goal point is x,y of target
    path = dc.PathSegment(obj, goal)  # heading straight for target

    # path_vars holds parameters for computing points in a path
    # TODO: try and make this more elegant
    path_vars = dc.PathVars(CLOCK_TICK, obj.speed, EVASIVE_PATH_ANGLE)

    #########################################################
    #  Loop while our object is active
    #########################################################
    while True:
        # always start with current position/state from the wmclient
        obj = wmclient.get_named_object(obj_name)

        # PATH PLANNING
        if obj:
            path_vars.increment_tick()  # increment clock
            if path_planning == "avoid":
                recompute_path = False
                sensors = wmclient.get_sensors(
                    obj_name, dc.DEFAULT_SCANRANGE
                )  # read sensors

                # compute next point, flag path for recompute if obstacle avoided
                next_point, recompute_path = plan_next_point_with_avoidance(
                    path, path_vars, obj, sensors
                )
                obj.set_point(next_point)  # update current object with next point
                if recompute_path is True:
                    path = dc.PathSegment(obj, goal)  # adjust path due to avoidance

            elif path_planning == "simple":
                next_point = plan_next_point_simple(path, path_vars, obj)
                obj.set_point(next_point)  # update current object with next point

            # move to computed next point
            wmclient.set_named_object(obj)  # send updated object to world model server
            wmclient.exit_if_dead(obj_name)

        time.sleep(CLOCK_TICK)


if __name__ == "__main__":
    main()

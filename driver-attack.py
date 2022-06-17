import defendercommon as dc
import euclid as eu
import numpy as np
import requests as req
import json
import time
import math as m
import sys

RETRY_PERIOD = 10.0  # delay if we're not connecting to server
CLOCK_TICK = 0.05
MY_SPEED = 25


# rotate a line segment about its p1 through an angle in degrees
def rotate_segment(cur_pt: dc.Point, nxt_pt: dc.Point, angle_deg: float) -> dc.Point:
    dx = nxt_pt.x - cur_pt.x
    dy = nxt_pt.y - cur_pt.y
    dr = nxt_pt.rotation - cur_pt.rotation
    delta_pt = dc.Point(dx, dy, dr)
    rho, phi = delta_pt.car2pol()
    phi += angle_deg
    new_x, new_y = delta_pt.pol2car(rho, phi)
    # add the current point back in
    new_x += cur_pt.x
    new_y += cur_pt.y
    new_r = nxt_pt.rotation
    new_point = dc.Point(new_x, new_y, new_r)
    return new_point


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
                next_point = rotate_segment(
                    current_point, next_point, path_vars.delta_path_angle
                )
                recompute_path = True
    return next_point, recompute_path


def set_goal_point(wmclient: dc.DriverRestClient) -> dc.Point:
    """Return a goal point that points to the target"""
    """ This should be set by some other means, but will do for now"""
    target = wmclient.get_target()
    return dc.Point(target.x, target.y, target.rotation)


def usage_and_exit(app_name):
    print(f"{app_name} <obj_name> [server IP:port | multicast]")
    print("<obj_name> must be a valid object")
    sys.exit()


def main():

    if len(sys.argv) < 2:
        usage_and_exit(sys.argv[0])

    # get name of object to move around in world-model and IP address
    obj_name = sys.argv[1]
    server_address = dc.DEFAULT_SERVER_ADDRESS  # set default worldserver address
    if len(sys.argv) >= 3:
        server_address = "http://" + sys.argv[2]

    # Create rest client (wmclient) to talk to world model server
    wmclient = dc.DriverRestClient(server_address)

    # Wait until World Model REST server becomes available
    wmclient.wait_for_server()

    # Get the object and sensor state of the object we're controlling (an attacker)
    wmclient.set_speed(obj_name, MY_SPEED)
    obj = wmclient.get_named_object(obj_name)  # this is the object we're controlling
    sensors = wmclient.get_sensors(obj_name, 100)  # the obstacles it can see

    # create a path segment between current point and goal point
    goal = set_goal_point(wmclient)
    path_vars = dc.PathVars(CLOCK_TICK, MY_SPEED)
    path = dc.PathSegment(obj, goal)

    # set path variables. delta_t and speed must be set first
    path_vars = path.compute_path_vars(path_vars)
    path_vars.delta_path_angle = 30.0  # only used in obstacle avoidance

    # loop while object isn't dead
    while True:
        # get current position/state
        obj = wmclient.get_named_object(obj_name)

        # path_planning = "obstacle_avoidance"
        path_planning = "simple"
        if obj:
            path_vars.increment_tick()  # increment clock
            if path_planning == "obstacle_avoidance":
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

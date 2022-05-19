from ast import Pass
from asyncore import poll
from flask_restful import abort
import requests
import json
import time
import math
import sys
import server_ip_multicast

# set some parameters
MAX_SPEED=10    # maximum speed we can move
DELTA_T=0.25    # main loop period
RETRY_PERIOD=10 # delay if we're not connecting to server
GOAL=[{'x':295},{'y':50}]
DEFAULT_SERVER_ADDRESS='http://worldserver:5000'
OBJECT_API_PATH='/v1/objects/name/'
SENSOR_API_PATH='/v1/sensors/name'
SCANRANGE=200
OBJECT_NAME=''
OBJECT_STATE=None
SENSOR_STATE=None
OBJECT_STATE_URL=''
SENSOR_STATE_URL=''

def get_object_state() -> dict:
    try:
        rsp = requests.get(OBJECT_STATE_URL)

        state = json.loads(rsp.text)
        return state
    except:
        print(f'failed to connect to server {OBJECT_STATE_URL}')
        return None
    
def get_sensor_state() -> dict:
    try:
        rsp = requests.get(OBJECT_STATE_URL)
        sensor_scan = json.loads(rsp.text)
        return sensor_scan
    except:
        print(f'failed to connect to server {SENSOR_STATE_URL}')
        return None

def set_state(state):
    requests.put(OBJECT_STATE_URL, data=state)

def wait_for_server(poll_period=RETRY_PERIOD)->dict:
    state = get_object_state()
    if state:
        return state
    else:    
        while state is None:
            time.sleep(poll_period)
            state=get_object_state()
            

def set_initial_state(state, speed=MAX_SPEED)->dict:
    # check to see if speed has already been set, otherwise set it
    # speed, position and rotation are state variables and should remain the same
    if state['speed']==0:
        state['speed']=speed
    return state

def modify_state(state) -> dict:
    global step_state, dstep
    
    max_move = MAX_SPEED * DELTA_T

    x = state['x']
    y = state['y']
    angle=math.radians(float(state['rotation'])-90.0)

    dx = max_move*math.cos(angle)
    dy = max_move*math.sin(angle)

    state["x"] = x + dx
    state["y"] = y + dy
    
    return state 


def sense_environment(state,sensors):
    global OBJECT_STATE,SENSOR_STATE
    
    return

def plan_path():
    global OBJECT_STATE
    pass

def execute_plan():
    global OBJECT_STATE
    pass

def abort_if_dead():
    if OBJECT_STATE['status'] == 'dead':
        sys.exit({"status":"Object is Dead"})

def abort_if_outofbounds():
    pass

def usage_and_exit(app_name):
    print (f"{app_name} <object_name> [server IP:port | multicast]")
    print ("<object_name> must be a valid object")
    sys.exit()

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        usage_and_exit(sys.argv[0])

    # get name of object to move around in world-model 
    OBJECT_NAME=sys.argv[1]

    # check for IP or multicast
    server_address=DEFAULT_SERVER_ADDRESS  # set default worldserver address
    if len(sys.argv) == 3:
        if sys.argv[2] == 'multicast':
            server_address=server_ip_multicast.wait_forever_for_server_address()
        else:
            server_address='http://' + sys.argv[2]
        
    OBJECT_STATE_URL= server_address + OBJECT_API_PATH + OBJECT_NAME
    SENSOR_STATE_URL= server_address + SENSOR_API_PATH + OBJECT_NAME + "?scanrange=" + SCANRANGE
    print (f"{OBJECT_NAME} driver connecting to {server_address} using full API path {OBJECT_STATE_URL}")
    print (f"{OBJECT_NAME} scanning from {server_address} using full API path {SENSOR_STATE_URL}")

    # get initial state, initial sensor readings and set object speed
    wait_for_server()
    OBJECT_STATE=get_object_state()
    SENSOR_STATE=get_sensor_state()
    OBJECT_STATE=set_initial_state(OBJECT_STATE,MAX_SPEED)
    

    while True:
        OBJECT_STATE=get_object_state(OBJECT_STATE)
        if OBJECT_STATE:
            sense_environment()
            plan_path()
            execute_plan()
            abort_if_outofbounds()
            abort_if_dead()
    
        time.sleep(DELTA_T)




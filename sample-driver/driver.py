from flask_restful import abort
import requests
import json
import time
import math
import sys

import debugpy
debugpy.listen(5678)

BASE_URL='http://127.0.0.1:5000/v1/objects/name/'
URL=''

def get_state() -> dict:
    rsp = requests.get(URL)
    state = json.loads(rsp.text)
    return state

def set_state(state):
    requests.put(URL, data=state)

step_state = 0
dstep = math.pi/180.0

def modify_state(state) -> dict:
    global step_state, dstep
    R = 200
    
    base_x = 500
    base_y = 500
    base_rotation = -180 

    dx = R*math.cos(step_state)
    dy = R*math.sin(step_state)

    state["x"] = str(int(base_x + dx))
    state["y"] = str(int(base_y + dy))
    state["rotation"] = str(int(base_rotation + math.degrees(step_state)))

    
    

    step_state += dstep
    

    return state

def usage():
    print ("driver.py <object_name>")
    print ("<object_name> must be a valid object")
    sys.exit()

if __name__ == "__main__":

    if (len(sys.argv) >= 2):
        URL=BASE_URL+sys.argv[1]
    else:
        usage()

    while True:
        state = get_state()
        state = modify_state(state)
        set_state(state)
        time.sleep(0.25)
        if state['state'] == 'dead':
            print (sys.argv[1] + "died due to collision!")
            sys.exit


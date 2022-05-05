import requests
import json
import time
import math

BASE_URL='http://127.0.0.1:5000/v1/objects/name/defender03'

def get_state() -> dict:
    rsp = requests.get(BASE_URL)
    state = json.loads(rsp.text)
    return state

def set_state(state):
    requests.put(BASE_URL, data=state)

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

if __name__ == "__main__":
    while True:
        state = get_state()
        state = modify_state(state)
        set_state(state)
        time.sleep(0.25)


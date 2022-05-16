from flask_restful import abort
import requests
import json
import time
import math
import sys
import server_ip_multicast

API_PATH='/v1/objects/name/'
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

def usage_and_exit(app_name):
    print (app_name + " <object_name> [server IP:port | multicast]")
    print ("<object_name> must be a valid object")
    sys.exit()

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        usage_and_exit(sys.argv[0])

    # get name of object to move around in world-model 
    object_name=sys.argv[1]

    # check for IP or multicast
    server_address="http://worldserver:5000"  # set default worldserver address
    if len(sys.argv) == 3:
        if sys.argv[2] == 'multicast':
            server_address=server_ip_multicast.wait_forever_for_server_address()
        else:
            server_address='http://' + sys.argv[2]
        
    URL= server_address + API_PATH + object_name
    print ("Connecting to server at " + server_address + " using full API path " + URL)
    
    while True:
        retry_period=5
        state={'state':'init'}
        try:
            state = get_state()
            state = modify_state(state)
            set_state(state)
            time.sleep(0.25)
        except:
            print(f'failed to connect to server {URL} retrying in {retry_period} seconds')
            time.sleep(retry_period)

        if state['state'] == 'dead':
            print (sys.argv[1] + " died due to collision!")
            sys.exit({"status":"Object is Dead"})


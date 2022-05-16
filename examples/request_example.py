import requests
import json
import time
from yaml import load,dump

BASE_URL='http://127.0.0.1:5000/'
configfile = "render-config.yaml"


if __name__ == "__main__":
    with open(configfile) as file:
            config_dict = yaml.load(file)
            
    while True:
        attackers=requests.get(BASE_URL + 'v1/objects/types/attacker')
        defenders=requests.get(BASE_URL + 'v1/objects/types/defender')
        obstacles=requests.get(BASE_URL + 'v1/objects/types/obstacle')
        targets=requests.get(BASE_URL + 'v1/objects/types/target')

        print (attackers.text)
        print (defenders.text)
        print (obstacles.text)
        print (targets.text)
        time.sleep(10)


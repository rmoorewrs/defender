export SERVER_IP=172.17.0.3
export SERVER_PORT=5000
export PATH_PLAN=avoid
export ATT01=config/attacker01.json
export ATT02=config/attacker02.json
export ATT03=config/attacker03.json

docker container run --rm --name attacker03 \
	-e SERVER_IP=$SERVER_IP \
	-e SERVER_PORT=$SERVER_PORT \
	-e CONFIG_FILE=$ATT03 \
	-e PATH_TYPE=$PATH_PLAN \
	defender-driver &

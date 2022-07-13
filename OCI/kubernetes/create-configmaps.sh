# create configmaps for each pod
kubectl create configmap configmap-defender-server --from-env-file=configmap/defender-server.properties
kubectl create configmap configmap-attacker01 --from-env-file=configmap/attacker01-env.properties
kubectl create configmap configmap-attacker02 --from-env-file=configmap/attacker02-env.properties
kubectl create configmap configmap-attacker03 --from-env-file=configmap/attacker03-env.properties
kubectl create configmap configmap-defender01 --from-env-file=configmap/defender01-env.properties
kubectl create configmap configmap-defender02 --from-env-file=configmap/defender02-env.properties
kubectl create configmap configmap-defender03 --from-env-file=configmap/defender03-env.properties

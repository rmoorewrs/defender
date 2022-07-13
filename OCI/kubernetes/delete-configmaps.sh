#create configmaps for each pod
kubectl delete configmap configmap-defender-server
kubectl delete configmap configmap-attacker01
kubectl delete configmap configmap-attacker02
kubectl delete configmap configmap-attacker03
kubectl delete configmap configmap-defender01
kubectl delete configmap configmap-defender02
kubectl delete configmap configmap-defender03

kubectl label nodes --all openwhisk-role=invoker

cd openwhisk-deploy-kube/

kubectl create ns openwhisk
helm install openwhisk ./helm/openwhisk --namespace=openwhisk #-f mycluster.yaml

# generate a random password
PASSWORD=$(head -c 12 /dev/urandom | shasum| cut -d' ' -f1)
USER="admin"

echo "User: ${USER}"
echo "Password: ${PASSWORD}"

# Create Namespaces for OpenFaaS
kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml

kubectl -n openfaas create secret generic basic-auth \
  --from-literal=basic-auth-user=${USER} \
  --from-literal=basic-auth-password=${PASSWORD}

# Install OpenFaaS

helm upgrade openfaas --install openfaas/openfaas \
  --namespace openfaas  \
  --set basic_auth=true \
  --set functionNamespace=openfaas-fn

OPENFAAS_URL=$(minikube ip):31112

echo "OpenFaaS Platform URL: ${OPENFAAS_URL}\n"

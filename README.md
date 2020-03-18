# Investigating possibilites for protecting and hardening installable FaaS platforms 

In this repository, a function is prepared to investigate function containers for various FaaS platforms regarding security.
Currently, function containers are investigated regarding read-only filesystems and if they are run with a root or non-root user.
For all the various FaaS platforms, setup steps are provided to get the function running on a minikube cluster.

# Prerequisites

* minikube (v1.4.0)
* kubectl (v1.16.1)
* helm (v3.0.0)
* glooctl ([>= v1.2.18](https://github.com/solo-io/gloo/releases))

CLI tools to interact with the FaaS platforms:

* Fission CLI tool, fission (>= v1.6.0)
* OpenFaaS CLI tool, faas-cli (>= 0.9.3)
* Kubeless CLI tool, kubeless (>= v1.0.4)
* OpenWhisk CLI tools, wsk and wskdeploy (>= 1.0.0)

# Setup

* Start with a new cluster:
  > minikube start

* Setup your helm repositories:
  > helm repo add openfaas https://openfaas.github.io/faas-netes/

  > helm repo add gloo https://storage.googleapis.com/solo-public-helm

  > helm repo update

* Function to test container security (already prepared):

```python
import os
import time
import json

def evaluate(file_folder, filename, file_content):

    # check for read-only filesystem
    read_only_filesystem = False
    try:
        with open('{0}/{1}'.format(file_folder, filename), 'w+') as file:
            file.write(file_content)
    except IOError:
        read_only_filesystem = True

    # check container user
    user = os.popen('whoami').read().rstrip()

    return json.dumps({'whoami': user, 'read-only-fs': read_only_filesystem})
```

## Fission

* Create a namespace for Fission
  > kubectl create namespace fission

* Deploy the Fission platform on the cluster
  > cd fission/ && ./install.sh

* Wait til Fission components are ready before continuing (at least controller)
  > kubectl get pods --namespace fission --watch

* Create an environment for the function
  > fission env create --name python --image fission/python-env --builder fission/python-builder

* Create a Function Package
  > zip -jr evaluate-container.zip evaluate-container/
  > fission package create --sourcearchive evaluate-container.zip --env python

* See if the package is deployed
  > fission pkg info --name {package-name}

* Deploy and test function
  > fission fn create --name evaluate-container --pkg {package-name} --entrypoint "function.main"

  Wait til function pools are available:

  > kubectl get pods --namespace fission-function

  then run your function

  > fission function test --name evaluate-container

## OpenFaaS

* Install OpenFaaS via shell script
  > cd openfaas/ && ./install.sh

* Wait until OpenFaaS has started:
  > kubectl -n openfaas get deployments -l "release=openfaas, app=openfaas" --watch

* Forward the OpenFaaS Gateway to your local machine (new terminal tab required)
  > kubectl port-forward svc/gateway -n openfaas 31112:8080 &

* Authenticate against the OpenFaaS platform to be able to deploy functions
  > faas-cli login --password {PASSWORD} --username admin --gateway http://127.0.0.1:31112

  The password was printed by the shell script of above. You can access the UI of the OpenFaaS platform over http://127.0.0.1:31112/ui/

* Pull the templates for the functions
  > faas-cli template pull

* (Optional) The following steps are only required when making changes to the function:
  > faas-cli build -f ./functions.yml

  The following command is required to push the image to Docker Hub. Please be careful which user is set within `functions.yaml`.

  > faas push --yaml functions.yml

* Pull and deploy the function
  
  > faas-cli deploy --yaml functions.yml

* Access the UI over http://127.0.0.1:31112/ui/ and invoke the function. Maybe you have to invoke the function twice, because of cold starts.

## Kubeless

* Install the Kubeless platform
  > cd kubeless/ && ./install.sh

* Create a function package
  > zip -jr evaluate-container.zip evaluate-container/

* Wait til Kubeless platform is up
  > kubectl get pods -n kubeless --watch

* Deploy your function package
  > kubeless function deploy evaluate-container --runtime python3.6 --from-file evaluate-container.zip --handler function.test

* (Optional) Check if function is ready (Troubleshooting)
  > kubeless function ls evaluate-container

  or using the following command:

  > kubectl get pods --watch

* Test your function
  > kubeless function call evaluate-container

## Knative

* Start your cluster with the following configuration
  > minikube start --memory=8192 --cpus=4 --disk-size=30g --extra-config=apiserver.enable-admission-plugins="LimitRanger,NamespaceExists,NamespaceLifecycle,ResourceQuota,ServiceAccount,DefaultStorageClass,MutatingAdmissionWebhook"

* Install Knative with glooctl
  > glooctl install knative -g

* Wait until Knative components are up
  > kubectl get pods -n knative-serving --watch

* Create namespace for gloo
  > kubectl create namespace gloo-system

* Install gloo
  > helm install gloo gloo/gloo --namespace gloo-system -f values.yaml

* Verify the gloo installation and wait until all components are up
  > kubectl get pods -n gloo-system --watch

* Make cluster services accessible on localhost (new tab is required)
  > minikube tunnel

* Configure DNS [as follows](https://knative.dev/docs/install/knative-with-gloo/#configuring-dns):
  
  Get external IP of `knative-external-proxy`:

  > kubectl get svc -ngloo-system

  Add this IP address to your DNS provider config:

  > KUBE_EDITOR="vim" kubectl edit cm config-domain --namespace knative-serving

  ```
  data:
    {{EXTERNAL_IP}}.xip.io: ""
  ```

* Deploy your function
  > kubectl apply --filename evaluate-container/function.yaml

* Find the URL of your function
  > kubectl get ksvc evaluate-container --output=custom-columns=NAME:.metadata.name,URL:.status.url

* Invoke your function
  > curl http://evaluate-container.default.10.109.224.178.xip.io

## OpenWhisk

* Clone OpenWhisk
  > git clone git@github.com:apache/openwhisk-deploy-kube.git

* Install the OpenWhisk platform
  > ./install.sh

* Configure your CLI Tool
  > minikube service list

  can be used to print the IP address and the port number of the entrypoint to OpenWhisk.

  > wsk property set --apihost {IP_ADDRESS_OF_OPENWISK_NGINX}:{PORT_OF_OPENWISK_NGINX}

  For Instance:

  > wsk property set --apihost 192.168.99.231:31001

  Then you also have to authenticate against the OpenWhisk platform:

  > wsk property set --auth 23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP

* Wait til all the OpenWhisk components are up
  > kubectl get pods --namespace openwhisk --watch

* Create a function package
  > zip -jr evaluate-container.zip evaluate-container/

* Deploy your function package
  > wsk action create evaluate-container -i --kind python:3 evaluate-container.zip

  Use `-i` to skip certificate validation.

* Invoke and test your function
  > wsk action invoke -i --result evaluate-container

# Function Outputs

## Fission

```json
{
    "read-only-fs": false,
    "whoami": "root"
}
```

## OpenFaaS

```json
{
    "read-only-fs": true,
    "whoami": "app"
}
```

## Kubeless

```json
{
    "read-only-fs": false,
    "whoami": ""
}
```

## Knative

```json
{
    "read-only-fs": false,
    "whoami": "function"
}
```

## OpenWisk

```json
{
    "read-only-fs": false,
    "whoami": "root"
}
```

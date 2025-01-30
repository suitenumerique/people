# Local development with Kubernetes

We use tilt to provide a local development environment for Kubernetes. 
Tilt is a tool that helps you develop applications for Kubernetes. 
It watches your files for changes, rebuilds your containers, and restarts your pods. 
It's like having a conversation with your cluster.


## Prerequisites

This guide assumes you have the following tools installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
  * [mkcert](https://github.com/FiloSottile/mkcert) 
- [ctlptl](https://github.com/tilt-dev/ctlptl)
- [Tilt](https://docs.tilt.dev/install.html)
  * [helm](https://helm.sh/docs/intro/install/)
  * [helmfile](https://github.com/helmfile/helmfile)
  * [secrets](https://github.com/jkroepke/helm-secrets/wiki/Installation)
  * [sops](https://github.com/getsops/sops)


### SOPS configuration

**Generate a SOPS key**

For this specific step you need to have the `age-keygen` tool installed.
See https://github.com/FiloSottile/age.
Then generate a key:

```bash
age-keygen -o my-age.key
```

**Install the SOPS key**

Read the SOPS documentation on how to install the key in your environment.
https://github.com/getsops/sops?tab=readme-ov-file#23encrypting-using-age

On Ubuntu it's like:

```bash
mkdir -p ~/.config/sops/age/
cp my-age.key ~/.config/sops/age/keys.txt
chmod 400 ~/.config/sops/age/keys.txt
```

**Add the SOPS key to the repository**

Update the [.sops.yaml](../.sops.yaml) file with the **public** key id you generated.


### Helmfile in Docker

If you use helmfile in Docker, you may need an additional configuration to make 
it work with you age key.

You need to `mount -v "${HOME}/.config/sops/age/:/helm/.config/sops/age/"`

```bash
#!/bin/sh

docker run --rm --net=host \
   -v "${HOME}/.kube:/root/.kube" \
   -v "${HOME}/.config/helm:/root/.config/helm" \
   -v "${HOME}/.config/sops/age/:/helm/.config/sops/age/" \
   -v "${HOME}/.minikube:/${HOME}/.minikube" \
   -v "${PWD}:/wd" \
   -e KUBECONFIG=/root/.kube/config \
   --workdir /wd ghcr.io/helmfile/helmfile:v0.150.0 helmfile "$@"
```


## Getting started

### Create the kubernetes cluster

Run the following command to create a kubernetes cluster using kind:

```bash
./bin/start-kind.sh
```

**or** run the equivalent using the makefile

```bash
make start-kind
```

### [Optional] Install the secret

You don't need to do this if you are running the stack with keycloak.

```bash
make install-external-secrets
```

### Deploy the application

```bash
# Pro Connect environment
tilt up -f ./bin/Tiltfile 

# Standalone environment with keycloak
DEV_ENV=dev-keycloak tilt up -f ./bin/Tiltfile
```

**or** run the equivalent using the makefile

```bash
# Pro Connect environment
make tilt-up

# Standalone environment with keycloak
make tilt-up-keycloak
```

That's it! You should now have a local development environment for Kubernetes.

You can access the application at https://desk.127.0.0.1.nip.io

## Management

To manage the cluster, you can use k9s.

## Next steps

- Add dimail to the local development environment
- Add a reset demo `cmd_button` to Tilt

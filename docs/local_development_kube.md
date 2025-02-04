# Local development with Kubernetes

We use tilt to provide a local development environment for Kubernetes. 
Tilt is a tool that helps you develop applications for Kubernetes. 
It watches your files for changes, rebuilds your containers, and restarts your pods. 
It's like having a conversation with your cluster.


## Prerequisites

This guide assumes you have the following tools installed:

- [brew](https://brew.sh/) if you are on linux
- [Docker](https://docs.docker.com/get-docker/)
- [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
  * [mkcert](https://github.com/FiloSottile/mkcert)
- [ctlptl](https://github.com/tilt-dev/ctlptl)
- [Tilt](https://docs.tilt.dev/install.html)
  * [helm](https://helm.sh/docs/intro/install/)
  * [helmfile](https://github.com/helmfile/helmfile)
  * [secrets](https://github.com/jkroepke/helm-secrets/wiki/Installation)

## Getting started

### Create the kubernetes cluster

Run the following command to create a kubernetes cluster using kind:

```bash
make start-kind
```

### Install the secret

You might not need to do this if you are run the stack with keycloak. 

```bash
make install-external-secrets
```

### Deploy the application

```bash
# Pro Connect environment
make tilt-up

# Standalone environment with keycloak
make start-tilt-keycloak
```

That's it! You should now have a local development environment for Kubernetes.

Wait for front-end image to build and you can access the application at https://desk.127.0.0.1.nip.io (it can take up to a few minutes)

## Management

To manage the cluster, you can use k9s.

## Next steps

- Add dimail to the local development environment
- Add a reset demo `cmd_button` to Tilt

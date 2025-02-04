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

[Install_prereq script](https://github.com/numerique-gouv/dk8s/blob/main/scripts/install-prereq.sh) (not tested).

## Create the kubernetes cluster

Run the following command to create a kubernetes cluster using kind:

```bash
make start-kind

# import your secrets from credentials manager
# ! don't forget "https" before your url
make install-external-secrets
```

That's it! You should now have a local development environment for Kubernetes.

## Start the application

```bash
# You can either start :
# ProConnect stack (but secrets must be set on your local cluster)
make tilt-up

# or standalone environment with keycloak
make start-tilt-keycloak
```

Access your application at https://desk.127.0.0.1.nip.io 

## Management

To manage the cluster, you can use k9s.

## Next steps

- Add dimail to the local development environment
- Add a reset demo `cmd_button` to Tilt

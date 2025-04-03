# Desk helm chart

## Parameters

### General configuration

| Name                                       | Description                                          | Value                    |
| ------------------------------------------ | ---------------------------------------------------- | ------------------------ |
| `image.repository`                         | Repository to use to pull desk's container image     | `lasuite/people-backend` |
| `image.tag`                                | desk's container tag                                 | `latest`                 |
| `image.pullPolicy`                         | Container image pull policy                          | `IfNotPresent`           |
| `image.credentials.username`               | Username for container registry authentication       |                          |
| `image.credentials.password`               | Password for container registry authentication       |                          |
| `image.credentials.registry`               | Registry url for which the credentials are specified |                          |
| `image.credentials.name`                   | Name of the generated secret for imagePullSecrets    |                          |
| `nameOverride`                             | Override the chart name                              | `""`                     |
| `fullnameOverride`                         | Override the full application name                   | `""`                     |
| `ingress.enabled`                          | whether to enable the Ingress or not                 | `false`                  |
| `ingress.className`                        | IngressClass to use for the Ingress                  | `nil`                    |
| `ingress.host`                             | Host for the Ingress                                 | `desk.example.com`       |
| `ingress.path`                             | Path to use for the Ingress                          | `/`                      |
| `ingress.hosts`                            | Additional host to configure for the Ingress         | `[]`                     |
| `ingress.tls.enabled`                      | Weather to enable TLS for the Ingress                | `true`                   |
| `ingress.tls.additional[].secretName`      | Secret name for additional TLS config                |                          |
| `ingress.tls.additional[].hosts[]`         | Hosts for additional TLS config                      |                          |
| `ingress.customBackends`                   | Add custom backends to ingress                       | `[]`                     |
| `ingressAdmin.enabled`                     | whether to enable the Ingress or not                 | `false`                  |
| `ingressAdmin.className`                   | IngressClass to use for the Ingress                  | `nil`                    |
| `ingressAdmin.host`                        | Host for the Ingress                                 | `desk.example.com`       |
| `ingressAdmin.path`                        | Path to use for the Ingress                          | `/admin`                 |
| `ingressAdmin.hosts`                       | Additional host to configure for the Ingress         | `[]`                     |
| `ingressAdmin.tls.enabled`                 | Weather to enable TLS for the Ingress                | `true`                   |
| `ingressAdmin.tls.additional[].secretName` | Secret name for additional TLS config                |                          |
| `ingressAdmin.tls.additional[].hosts[]`    | Hosts for additional TLS config                      |                          |

### backend

| Name                                                  | Description                                                                        | Value                                                                            |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `backend.pdb.enabled`                                 | Enable pdb on backend                                                              | `true`                                                                           |
| `backend.dpAnnotations`                               | Annotations to add to the backend Deployment                                       | `{}`                                                                             |
| `backend.command`                                     | Override the backend container command                                             | `[]`                                                                             |
| `backend.args`                                        | Override the backend container args                                                | `[]`                                                                             |
| `backend.replicas`                                    | Amount of backend replicas                                                         | `3`                                                                              |
| `backend.shareProcessNamespace`                       | Enable share process namespace between containers                                  | `false`                                                                          |
| `backend.sidecars`                                    | Add sidecars containers to backend deployment                                      | `[]`                                                                             |
| `backend.migrateJobAnnotations`                       | Annotations for the migrate job                                                    | `{}`                                                                             |
| `backend.securityContext`                             | Configure backend Pod security context                                             | `nil`                                                                            |
| `backend.envVars`                                     | Configure backend container environment variables                                  | `undefined`                                                                      |
| `backend.envVars.BY_VALUE`                            | Example environment variable by setting value directly                             |                                                                                  |
| `backend.envVars.FROM_CONFIGMAP.configMapKeyRef.name` | Name of a ConfigMap when configuring env vars from a ConfigMap                     |                                                                                  |
| `backend.envVars.FROM_CONFIGMAP.configMapKeyRef.key`  | Key within a ConfigMap when configuring env vars from a ConfigMap                  |                                                                                  |
| `backend.envVars.FROM_SECRET.secretKeyRef.name`       | Name of a Secret when configuring env vars from a Secret                           |                                                                                  |
| `backend.envVars.FROM_SECRET.secretKeyRef.key`        | Key within a Secret when configuring env vars from a Secret                        |                                                                                  |
| `backend.podAnnotations`                              | Annotations to add to the backend Pod                                              | `{}`                                                                             |
| `backend.service.type`                                | backend Service type                                                               | `ClusterIP`                                                                      |
| `backend.service.port`                                | backend Service listening port                                                     | `80`                                                                             |
| `backend.service.targetPort`                          | backend container listening port                                                   | `8000`                                                                           |
| `backend.service.annotations`                         | Annotations to add to the backend Service                                          | `{}`                                                                             |
| `backend.migrate.command`                             | backend migrate command                                                            | `["python","manage.py","migrate","--no-input"]`                                  |
| `backend.migrate.restartPolicy`                       | backend migrate job restart policy                                                 | `Never`                                                                          |
| `backend.probes.liveness.path`                        | Configure path for backend HTTP liveness probe                                     | `/__heartbeat__`                                                                 |
| `backend.probes.liveness.targetPort`                  | Configure port for backend HTTP liveness probe                                     | `undefined`                                                                      |
| `backend.probes.liveness.initialDelaySeconds`         | Configure initial delay for backend liveness probe                                 | `10`                                                                             |
| `backend.probes.liveness.initialDelaySeconds`         | Configure timeout for backend liveness probe                                       | `10`                                                                             |
| `backend.probes.startup.path`                         | Configure path for backend HTTP startup probe                                      | `undefined`                                                                      |
| `backend.probes.startup.targetPort`                   | Configure port for backend HTTP startup probe                                      | `undefined`                                                                      |
| `backend.probes.startup.initialDelaySeconds`          | Configure initial delay for backend startup probe                                  | `undefined`                                                                      |
| `backend.probes.startup.initialDelaySeconds`          | Configure timeout for backend startup probe                                        | `undefined`                                                                      |
| `backend.probes.readiness.path`                       | Configure path for backend HTTP readiness probe                                    | `/__lbheartbeat__`                                                               |
| `backend.probes.readiness.targetPort`                 | Configure port for backend HTTP readiness probe                                    | `undefined`                                                                      |
| `backend.probes.readiness.initialDelaySeconds`        | Configure initial delay for backend readiness probe                                | `10`                                                                             |
| `backend.probes.readiness.initialDelaySeconds`        | Configure timeout for backend readiness probe                                      | `10`                                                                             |
| `backend.resources`                                   | Resource requirements for the backend container                                    | `{}`                                                                             |
| `backend.nodeSelector`                                | Node selector for the backend Pod                                                  | `{}`                                                                             |
| `backend.tolerations`                                 | Tolerations for the backend Pod                                                    | `[]`                                                                             |
| `backend.affinity`                                    | Affinity for the backend Pod                                                       | `{}`                                                                             |
| `backend.persistence`                                 | Additional volumes to create and mount on the backend. Used for debugging purposes | `{}`                                                                             |
| `backend.persistence.volume-name.size`                | Size of the additional volume                                                      |                                                                                  |
| `backend.persistence.volume-name.type`                | Type of the additional volume, persistentVolumeClaim or emptyDir                   |                                                                                  |
| `backend.persistence.volume-name.mountPath`           | Path where the volume should be mounted to                                         |                                                                                  |
| `backend.extraVolumeMounts`                           | Additional volumes to mount on the backend.                                        | `[]`                                                                             |
| `backend.extraVolumes`                                | Additional volumes to mount on the backend.                                        | `[]`                                                                             |
| `backend.createsuperuser.command`                     | The command to create the django super user                                        | `python manage.py createsuperuser --username admin@example.com --password admin` |
| `backend.createsuperuser.enabled`                     | Whether to create the superuser job                                                | `true`                                                                           |
| `backend.createsuperuser.restartPolicy`               | The restart policy for the job                                                     | `Never`                                                                          |

### frontend

| Name                                                   | Description                                                                         | Value                     |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------- | ------------------------- |
| `frontend.pdb.enabled`                                 | Enable pdb on backend                                                               | `true`                    |
| `frontend.image.repository`                            | Repository to use to pull desk's frontend container image                           | `lasuite/people-frontend` |
| `frontend.image.tag`                                   | desk's frontend container tag                                                       | `latest`                  |
| `frontend.image.pullPolicy`                            | frontend container image pull policy                                                | `IfNotPresent`            |
| `frontend.dpAnnotations`                               | Annotations to add to the frontend Deployment                                       | `{}`                      |
| `frontend.command`                                     | Override the frontend container command                                             | `[]`                      |
| `frontend.args`                                        | Override the frontend container args                                                | `[]`                      |
| `frontend.replicas`                                    | Amount of frontend replicas                                                         | `3`                       |
| `frontend.shareProcessNamespace`                       | Enable share process namefrontend between containers                                | `false`                   |
| `frontend.sidecars`                                    | Add sidecars containers to frontend deployment                                      | `[]`                      |
| `frontend.securityContext`                             | Configure frontend Pod security context                                             | `nil`                     |
| `frontend.envVars`                                     | Configure frontend container environment variables                                  | `undefined`               |
| `frontend.envVars.BY_VALUE`                            | Example environment variable by setting value directly                              |                           |
| `frontend.envVars.FROM_CONFIGMAP.configMapKeyRef.name` | Name of a ConfigMap when configuring env vars from a ConfigMap                      |                           |
| `frontend.envVars.FROM_CONFIGMAP.configMapKeyRef.key`  | Key within a ConfigMap when configuring env vars from a ConfigMap                   |                           |
| `frontend.envVars.FROM_SECRET.secretKeyRef.name`       | Name of a Secret when configuring env vars from a Secret                            |                           |
| `frontend.envVars.FROM_SECRET.secretKeyRef.key`        | Key within a Secret when configuring env vars from a Secret                         |                           |
| `frontend.podAnnotations`                              | Annotations to add to the frontend Pod                                              | `{}`                      |
| `frontend.service.type`                                | frontend Service type                                                               | `ClusterIP`               |
| `frontend.service.port`                                | frontend Service listening port                                                     | `80`                      |
| `frontend.service.targetPort`                          | frontend container listening port                                                   | `8080`                    |
| `frontend.service.annotations`                         | Annotations to add to the frontend Service                                          | `{}`                      |
| `frontend.probes`                                      | Configure probe for frontend                                                        | `{}`                      |
| `frontend.probes.liveness.path`                        | Configure path for frontend HTTP liveness probe                                     |                           |
| `frontend.probes.liveness.targetPort`                  | Configure port for frontend HTTP liveness probe                                     |                           |
| `frontend.probes.liveness.initialDelaySeconds`         | Configure initial delay for frontend liveness probe                                 |                           |
| `frontend.probes.liveness.initialDelaySeconds`         | Configure timeout for frontend liveness probe                                       |                           |
| `frontend.probes.startup.path`                         | Configure path for frontend HTTP startup probe                                      |                           |
| `frontend.probes.startup.targetPort`                   | Configure port for frontend HTTP startup probe                                      |                           |
| `frontend.probes.startup.initialDelaySeconds`          | Configure initial delay for frontend startup probe                                  |                           |
| `frontend.probes.startup.initialDelaySeconds`          | Configure timeout for frontend startup probe                                        |                           |
| `frontend.probes.readiness.path`                       | Configure path for frontend HTTP readiness probe                                    |                           |
| `frontend.probes.readiness.targetPort`                 | Configure port for frontend HTTP readiness probe                                    |                           |
| `frontend.probes.readiness.initialDelaySeconds`        | Configure initial delay for frontend readiness probe                                |                           |
| `frontend.probes.readiness.initialDelaySeconds`        | Configure timeout for frontend readiness probe                                      |                           |
| `frontend.resources`                                   | Resource requirements for the frontend container                                    | `{}`                      |
| `frontend.nodeSelector`                                | Node selector for the frontend Pod                                                  | `{}`                      |
| `frontend.tolerations`                                 | Tolerations for the frontend Pod                                                    | `[]`                      |
| `frontend.affinity`                                    | Affinity for the frontend Pod                                                       | `{}`                      |
| `frontend.persistence`                                 | Additional volumes to create and mount on the frontend. Used for debugging purposes | `{}`                      |
| `frontend.persistence.volume-name.size`                | Size of the additional volume                                                       |                           |
| `frontend.persistence.volume-name.type`                | Type of the additional volume, persistentVolumeClaim or emptyDir                    |                           |
| `frontend.persistence.volume-name.mountPath`           | Path where the volume should be mounted to                                          |                           |
| `frontend.extraVolumeMounts`                           | Additional volumes to mount on the frontend.                                        | `[]`                      |
| `frontend.extraVolumes`                                | Additional volumes to mount on the frontend.                                        | `[]`                      |

### celeryWorker

| Name                                                       | Description                                                                             | Value                                          |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `celeryWorker.dpAnnotations`                               | Annotations to add to the celeryWorker Deployment                                       | `{}`                                           |
| `celeryWorker.command`                                     | Override the celeryWorker container command                                             | `["celery","-A","people.celery_app","worker"]` |
| `celeryWorker.args`                                        | Override the celeryWorker container args                                                | `[]`                                           |
| `celeryWorker.replicas`                                    | Amount of celeryWorker replicas                                                         | `1`                                            |
| `celeryWorker.shareProcessNamespace`                       | Enable share process namespace between containers                                       | `false`                                        |
| `celeryWorker.sidecars`                                    | Add sidecars containers to celeryWorker deployment                                      | `[]`                                           |
| `celeryWorker.migrateJobAnnotations`                       | Annotations for the migrate job                                                         | `{}`                                           |
| `celeryWorker.securityContext`                             | Configure celeryWorker Pod security context                                             | `nil`                                          |
| `celeryWorker.envVars`                                     | Configure celeryWorker container environment variables                                  | `undefined`                                    |
| `celeryWorker.envVars.BY_VALUE`                            | Example environment variable by setting value directly                                  |                                                |
| `celeryWorker.envVars.FROM_CONFIGMAP.configMapKeyRef.name` | Name of a ConfigMap when configuring env vars from a ConfigMap                          |                                                |
| `celeryWorker.envVars.FROM_CONFIGMAP.configMapKeyRef.key`  | Key within a ConfigMap when configuring env vars from a ConfigMap                       |                                                |
| `celeryWorker.envVars.FROM_SECRET.secretKeyRef.name`       | Name of a Secret when configuring env vars from a Secret                                |                                                |
| `celeryWorker.envVars.FROM_SECRET.secretKeyRef.key`        | Key within a Secret when configuring env vars from a Secret                             |                                                |
| `celeryWorker.podAnnotations`                              | Annotations to add to the celeryWorker Pod                                              | `{}`                                           |
| `celeryWorker.probes`                                      | Configure celeryWorker probes                                                           | `{}`                                           |
| `celeryWorker.probes.liveness.path`                        | Configure path for celeryWorker HTTP liveness probe                                     | `undefined`                                    |
| `celeryWorker.probes.liveness.targetPort`                  | Configure port for celeryWorker HTTP liveness probe                                     | `undefined`                                    |
| `celeryWorker.probes.liveness.initialDelaySeconds`         | Configure initial delay for celeryWorker liveness probe                                 | `undefined`                                    |
| `celeryWorker.probes.liveness.initialDelaySeconds`         | Configure timeout for celeryWorker liveness probe                                       | `undefined`                                    |
| `celeryWorker.probes.startup.path`                         | Configure path for celeryWorker HTTP startup probe                                      | `undefined`                                    |
| `celeryWorker.probes.startup.targetPort`                   | Configure port for celeryWorker HTTP startup probe                                      | `undefined`                                    |
| `celeryWorker.probes.startup.initialDelaySeconds`          | Configure initial delay for celeryWorker startup probe                                  | `undefined`                                    |
| `celeryWorker.probes.startup.initialDelaySeconds`          | Configure timeout for celeryWorker startup probe                                        | `undefined`                                    |
| `celeryWorker.probes.readiness.path`                       | Configure path for celeryWorker HTTP readiness probe                                    | `undefined`                                    |
| `celeryWorker.probes.readiness.targetPort`                 | Configure port for celeryWorker HTTP readiness probe                                    | `undefined`                                    |
| `celeryWorker.probes.readiness.initialDelaySeconds`        | Configure initial delay for celeryWorker readiness probe                                | `undefined`                                    |
| `celeryWorker.probes.readiness.initialDelaySeconds`        | Configure timeout for celeryWorker readiness probe                                      | `undefined`                                    |
| `celeryWorker.resources`                                   | Resource requirements for the celeryWorker container                                    | `{}`                                           |
| `celeryWorker.nodeSelector`                                | Node selector for the celeryWorker Pod                                                  | `{}`                                           |
| `celeryWorker.tolerations`                                 | Tolerations for the celeryWorker Pod                                                    | `[]`                                           |
| `celeryWorker.affinity`                                    | Affinity for the celeryWorker Pod                                                       | `{}`                                           |
| `celeryWorker.persistence`                                 | Additional volumes to create and mount on the celeryWorker. Used for debugging purposes | `{}`                                           |
| `celeryWorker.persistence.volume-name.size`                | Size of the additional volume                                                           |                                                |
| `celeryWorker.persistence.volume-name.type`                | Type of the additional volume, persistentVolumeClaim or emptyDir                        |                                                |
| `celeryWorker.persistence.volume-name.mountPath`           | Path where the volume should be mounted to                                              |                                                |
| `celeryWorker.extraVolumeMounts`                           | Additional volumes to mount on the celeryWorker.                                        | `[]`                                           |
| `celeryWorker.extraVolumes`                                | Additional volumes to mount on the celeryWorker.                                        | `[]`                                           |

### celeryBeat

| Name                                                     | Description                                                                           | Value                                        |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------- |
| `celeryBeat.dpAnnotations`                               | Annotations to add to the celeryBeat Deployment                                       | `{}`                                         |
| `celeryBeat.command`                                     | Override the celeryBeat container command                                             | `["celery","-A","people.celery_app","beat"]` |
| `celeryBeat.args`                                        | Override the celeryBeat container args                                                | `[]`                                         |
| `celeryBeat.replicas`                                    | Amount of celeryBeat replicas                                                         | `1`                                          |
| `celeryBeat.shareProcessNamespace`                       | Enable share process namespace between containers                                     | `false`                                      |
| `celeryBeat.sidecars`                                    | Add sidecars containers to celeryBeat deployment                                      | `[]`                                         |
| `celeryBeat.securityContext`                             | Configure celeryBeat Pod security context                                             | `nil`                                        |
| `celeryBeat.envVars`                                     | Configure celeryBeat container environment variables                                  | `undefined`                                  |
| `celeryBeat.envVars.BY_VALUE`                            | Example environment variable by setting value directly                                |                                              |
| `celeryBeat.envVars.FROM_CONFIGMAP.configMapKeyRef.name` | Name of a ConfigMap when configuring env vars from a ConfigMap                        |                                              |
| `celeryBeat.envVars.FROM_CONFIGMAP.configMapKeyRef.key`  | Key within a ConfigMap when configuring env vars from a ConfigMap                     |                                              |
| `celeryBeat.envVars.FROM_SECRET.secretKeyRef.name`       | Name of a Secret when configuring env vars from a Secret                              |                                              |
| `celeryBeat.envVars.FROM_SECRET.secretKeyRef.key`        | Key within a Secret when configuring env vars from a Secret                           |                                              |
| `celeryBeat.probes`                                      | Configure celeryBeat probes                                                           | `{}`                                         |
| `celeryBeat.resources`                                   | Resource requirements for the celeryBeat container                                    | `{}`                                         |
| `celeryBeat.nodeSelector`                                | Node selector for the celeryBeat Pod                                                  | `{}`                                         |
| `celeryBeat.tolerations`                                 | Tolerations for the celeryBeat Pod                                                    | `[]`                                         |
| `celeryBeat.affinity`                                    | Affinity for the celeryBeat Pod                                                       | `{}`                                         |
| `celeryBeat.persistence`                                 | Additional volumes to create and mount on the celeryBeat. Used for debugging purposes | `{}`                                         |
| `celeryBeat.extraVolumeMounts`                           | Additional volumes to mount on the celeryBeat.                                        | `[]`                                         |
| `celeryBeat.extraVolumes`                                | Additional volumes to mount on the celeryBeat.                                        | `[]`                                         |

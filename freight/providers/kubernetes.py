__all__ = ["KubernetesProvider"]

from time import sleep
from functools import partial
from dataclasses import dataclass, asdict

from kubernetes import client
from kubernetes.config import new_client_from_config, ConfigException

from .base import Provider
from freight.models import App, Deploy


@dataclass(frozen=True)
class TaskContext:
    id: str
    date_created: str
    name: str
    environment: str
    sha: str
    prev_sha: str
    ref: str


class KubernetesProvider(Provider):
    def get_options(self):
        return {
            "steps": {"required": True, "type": list},
            "context": {"required": False, "type": str},
            "credentials": {"required": False, "type": dict},
        }

    def get_config(self, workspace, task):
        # from yaml import safe_load
        # TODO(mattrobenolt): Load and merge config (.freight.yml) from
        # within the workspace, so a config could be left out entirely.
        return {**task.provider_config, **{}}

    def execute(self, workspace, task):
        deploy = Deploy.query.filter(Deploy.task_id == task.id).first()
        return self.execute_deploy(workspace, deploy, task)

    def execute_deploy(self, workspace, deploy, task):
        app = App.query.get(task.app_id)
        prev_sha = app.get_previous_sha(deploy.environment, current_sha=task.sha)

        config = self.get_config(workspace, task)
        api_client = load_credentials(config)

        task_context = TaskContext(
            str(deploy.id),
            str(task.date_created),
            app.name,
            deploy.environment,
            task.sha,
            prev_sha or "",
            task.ref,
        )

        for step in config["steps"]:
            run_step(step, api_client, task_context)


def load_credentials(config):
    try:
        return new_client_from_config(context=config["context"])
    except KeyError:
        pass

    try:
        credentials = config["credentials"]
    except KeyError:
        return

    assert credentials["kind"] == "gcloud"

    return load_credentials_gcloud(credentials)


def load_credentials_gcloud(credentials):
    from subprocess import check_call, DEVNULL

    cluster = credentials["cluster"]
    project = credentials["project"]
    zone = credentials["zone"]

    context = f"gke_{project}_{zone}_{cluster}"

    try:
        return new_client_from_config(context=context)
    except ConfigException:
        pass

    check_call(
        [
            "gcloud",
            "container",
            "clusters",
            "get-credentials",
            cluster,
            "--zone",
            zone,
            "--project",
            project,
        ],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )

    return new_client_from_config(context=context)


def run_step(step, api_client, task):
    assert step["kind"] == "Deployment"
    watchers = run_step_deployment(step, api_client, task)
    changes = bool(watchers)
    while watchers:
        for watcher, state in watchers:
            status, success = watcher()
            last_status = state.get("status", None)
            if last_status is None or status != last_status:
                print(status)
                state["status"] = status
            if success:
                watchers.remove((watcher, state))
        sleep(0.5)
    return changes


def run_step_deployment(step, api_client, task):
    api = client.AppsV1beta1Api(api_client)

    selector = step["selector"]
    selector.setdefault("namespace", "default")
    containers = step["containers"]

    watchers = []

    for deployment in api.list_namespaced_deployment(**selector).items:
        namespace = deployment.metadata.name
        name = deployment.metadata.name
        changes = False
        for container in deployment.spec.template.spec.containers:
            for c in containers:
                if container.name == c["name"]:
                    container.image = c["image"].format(**asdict(task))
                    changes = True
        if changes:
            if deployment.metadata.annotations is None:
                deployment.metadata.annotations = {}
            if deployment.spec.template.metadata.annotations is None:
                deployment.spec.template.metadata.annotations = {}
            for k, v in asdict(task).items():
                deployment.metadata.annotations[f"freight.sentry.io/{k}"] = v
                deployment.spec.template.metadata.annotations[f"freight.sentry.io/{k}"] = v

            resp = api.patch_namespaced_deployment(
                name=deployment.metadata.name,
                namespace=deployment.metadata.namespace,
                body=deployment,
            )

            watchers.append(
                (
                    partial(
                        rollout_status_deployment,
                        api,
                        resp.metadata.name,
                        resp.metadata.namespace,
                        resp.metadata.generation,
                    ),
                    {},  # empty state dict for this rollout
                )
            )

    return watchers


def rollout_status_deployment(api, name, namespace, generation):
    # TODO(mattrobenolt): Need to handle error state better/at all.
    # Right now, if say, it's an ErrImagePull or something, it just will sit
    # here forever with no reason why. Need to figure out how to get
    # this reason becasue there are many reasons why it could fail.
    deployment = api.read_namespaced_deployment(name=name, namespace=namespace)
    if generation <= deployment.status.observed_generation:
        replicas = deployment.spec.replicas
        updated_replicas = deployment.status.updated_replicas or 0
        available_replicas = deployment.status.available_replicas or 0

        if updated_replicas < replicas:
            return (
                f"Waiting for deployment {repr(name)} rollout to finish: {updated_replicas} out of {replicas} new replicas have been updated...",
                False,
            )
        if replicas > updated_replicas:
            return (
                f"Waiting for deployment {repr(name)} rollout to finish: {replicas-updated_replicas} old replicas are pending termination...",
                False,
            )
        if available_replicas < updated_replicas:
            return (
                f"Waiting for deployment {repr(name)} rollout to finish: {available_replicas} of {updated_replicas} updated replicas are available...",
                False,
            )
        return f"Deployment {repr(name)} successfully rolled out", True

    return f"Waiting for deployment {repr(name)} spec update to be observed...", False

__all__ = ["PipelineProvider"]

import sys
from time import sleep, time
from typing import Optional, List, Callable
from functools import partial
from dataclasses import dataclass, asdict

from kubernetes import client
from kubernetes.config import new_client_from_config, ConfigException

from .base import Provider
from freight.utils.workspace import Workspace
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


@dataclass(frozen=True)
class KubernetesContext:
    client: client.ApiClient


@dataclass(frozen=True)
class PipelineContext:
    task: TaskContext
    kube: Optional[KubernetesContext]
    workspace: Workspace


class StepFailed(Exception):
    pass


class PipelineProvider(Provider):
    def get_options(self):
        return {
            "steps": {"required": True, "type": list},
            "kubernetes": {"required": False, "type": dict},
        }

    def get_config(self, workspace, task) -> dict:
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
        if config["kubernetes"]:
            kube_context = KubernetesContext(
                load_kube_credentials(config["kubernetes"])
            )
        else:
            kube_context = None

        task_context = TaskContext(
            str(deploy.id),
            str(task.date_created),
            app.name,
            deploy.environment,
            task.sha,
            prev_sha or "",
            task.ref,
        )

        context = PipelineContext(
            task=task_context, kube=kube_context, workspace=workspace
        )

        for i, step in enumerate(config["steps"]):
            workspace.log.info(f"Running Step {i+1} ({step['kind']})")
            run_step(step, context)
            workspace.log.info(f"Finished Step {i+1}")


def load_kube_credentials(config: dict) -> client.ApiClient:
    try:
        return new_client_from_config(context=config["context"])
    except KeyError:
        pass

    try:
        credentials = config["credentials"]
    except KeyError:
        return

    assert credentials["kind"] == "gcloud"

    return load_kube_credentials_gcloud(credentials)


def load_kube_credentials_gcloud(credentials: dict) -> client.ApiClient:
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


def run_step(step: dict, context: PipelineContext) -> bool:
    assert step["kind"] in ("Shell", "KubernetesDeployment", "KubernetesJob"), step["kind"]
    watchers = {
        "Shell": run_step_shell,
        "KubernetesDeployment": run_step_deployment,
        "KubernetesJob": run_step_job,
    }[step["kind"]](step, context)
    if not watchers:
        return
    changes = bool(watchers)
    while watchers:
        for watcher, state in watchers:
            status, success = watcher()
            last_status = state.get("status", None)
            if last_status is None or status != last_status:
                sys.stdout.write(status)
                sys.stdout.write("\n")
                sys.stdout.flush()
                state["status"] = status
            if success:
                watchers.remove((watcher, state))
                if not watchers:
                    break
        sleep(0.5)
    return changes


def run_step_deployment(step: dict, context: PipelineContext) -> List[Callable]:
    context.workspace.log.info(f"Running Deployment: {repr(step)}")

    api = client.AppsV1beta1Api(context.kube.client)

    selector = format_task(step["selector"], context.task)
    selector.setdefault("namespace", "default")
    containers = format_task(step["containers"], context.task)

    watchers = []

    for deployment in api.list_namespaced_deployment(**selector).items:
        namespace = deployment.metadata.name
        name = deployment.metadata.name
        changes = False
        for container in deployment.spec.template.spec.containers:
            for c in containers:
                if container.name == c["name"]:
                    container.image = c["image"]
                    changes = True
        if changes:
            if deployment.metadata.annotations is None:
                deployment.metadata.annotations = {}
            if deployment.spec.template.metadata.annotations is None:
                deployment.spec.template.metadata.annotations = {}
            for k, v in asdict(context.task).items():
                k = f"freight.sentry.io/{k}"
                deployment.metadata.annotations[k] = v
                deployment.spec.template.metadata.annotations[k] = v

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


def run_step_shell(step: dict, context: PipelineContext):
    command = format_task(step["command"], context.task)
    context.workspace.run(command, env=step.get("env"))


def format_task(data, task: TaskContext):
    if isinstance(data, str):
        return data.format(**asdict(task))
    if isinstance(data, list):
        return [format_task(d, task) for d in data]
    if isinstance(data, dict):
        return {k: format_task(v, task) for k, v in data.items()}
    return data


def make_job_spec(step: dict, task: TaskContext) -> dict:
    return {
        "kind": "Job",
        "metadata": {
            "name": f"{step['name']}-{int(time())}",
            "namespace": step.get("namespace", "default"),
        },
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": "job",
                            "image": format_task(step["image"], task),
                            "args": format_task(step.get("args", []), task),
                            "env": format_task(step.get("env", []), task),
                            "volumeMounts": step.get("volumeMounts", []),
                            "resources": step.get("resources", {}),
                        }
                    ],
                    "volumes": step.get("volumes", []),
                    "restartPolicy": "Never",
                }
            },
            "backoffLimit": 0,
        },
    }


def run_step_job(step: dict, context: PipelineContext):
    context.workspace.log.info(f"Running Job: {repr(step)}")

    job_spec = make_job_spec(step, context.task)
    name = job_spec["metadata"]["name"]
    namespace = job_spec["metadata"]["namespace"]

    context.workspace.log.info(f"Creating Job {namespace}/{name}")
    client.BatchV1Api(context.kube.client).create_namespaced_job(
        namespace=namespace, body=job_spec
    )
    pod_name = None
    try:
        pods = (
            client.CoreV1Api(context.kube.client)
            .list_namespaced_pod(namespace=namespace, label_selector=f"job-name={name}")
            .items
        )
        assert len(pods) == 1, len(pods)
        pod_name = pods[0].metadata.name
        context.workspace.log.info(f"Waiting for Pod {pod_name}")
        read_logs = False
        while True:
            pod = client.CoreV1Api(context.kube.client).read_namespaced_pod(
                namespace=namespace, name=pod_name
            )
            if read_logs:
                if pod.status.phase == "Failed":
                    raise StepFailed("Failed")
                break

            if pod.status.phase == "Pending":
                if (
                    pod.status.container_statuses[0].state.waiting.reason
                    == "ContainerCreating"
                ):
                    sleep(0.5)
                    continue
                else:
                    raise StepFailed(
                        pod.status.container_statuses[0].state.waiting.reason
                    )

            if pod.status.phase in ("Running", "Succeeded", "Failed"):
                resp = client.CoreV1Api(context.kube.client).read_namespaced_pod_log(
                    namespace=namespace,
                    name=pod_name,
                    follow=True,
                    _preload_content=False,
                )
                try:
                    for chunk in resp.stream(32):
                        sys.stdout.write(chunk.decode("utf8"))
                        sys.stdout.flush()
                finally:
                    resp.release_conn()
                sys.stdout.write("\n")
                sys.stdout.flush()
                read_logs = True
    finally:
        context.workspace.log.info(f"Deleting Job {namespace}/{name}")
        client.BatchV1Api(context.kube.client).delete_namespaced_job(
            namespace=namespace, name=name, propagation_policy="Foreground"
        )


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

__all__ = ["PipelineProvider"]

import sys
from time import sleep, time
from typing import Optional, List, Callable, Tuple
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


class AuthenticationError(Exception):
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
    # If a context is specified, attempt to use this first.
    try:
        return new_client_from_config(context=config["context"])
    except KeyError:
        pass

    try:
        credentials = config["credentials"]
    except KeyError:
        raise AuthenticationError("Missing kubernetes context.")

    if credentials["kind"] not in ("gcloud",):
        raise AuthenticationError(f"Unknown kubernetes kind: {credentials['kind']}")

    return load_kube_credentials_gcloud(credentials)


def load_kube_credentials_gcloud(credentials: dict) -> client.ApiClient:
    # Try to pull credentials from gcloud, but first checking if there
    # is a context, using their auto generated naming scheme, to avoid
    # calling `gcloud` every time, if we've already authed before.
    from subprocess import check_call, DEVNULL

    cluster = credentials["cluster"]
    project = credentials["project"]
    zone = credentials["zone"]

    context = f"gke_{project}_{zone}_{cluster}"

    try:
        return new_client_from_config(context=context)
    except (ConfigException, FileNotFoundError):
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


def run_step(step: dict, context: PipelineContext):
    if step["kind"] not in ("Shell", "KubernetesDeployment", "KubernetesJob"):
        raise StepFailed(f"Unknown step kind: {step['kind']}")

    watchers = {
        "Shell": run_step_shell,
        "KubernetesDeployment": run_step_deployment,
        "KubernetesJob": run_step_job,
    }[step["kind"]](step, context)
    if not watchers:
        return

    # Steps may return a list of "watchers". A watcher is meant to
    # watch over an async operation and wait until they are finished.

    # Iterate over all watchers, waiting for state to be True, and
    # printing out their status until they finish.
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
                    return
        sleep(0.5)


def run_step_deployment(step: dict, context: PipelineContext) -> List[Callable]:
    # Execute a Kubernetes Deployment
    context.workspace.log.info(f"Running Deployment: {repr(step)}")

    api = client.AppsV1beta1Api(context.kube.client)

    selector = format_task(step["selector"], context.task)
    selector.setdefault("namespace", "default")
    containers = format_task(step["containers"], context.task)

    watchers = []

    # First, we collect a list of Deployments from kubernetes based on
    # the `selector`. This may return 0, 1, or many Deployments.

    # For each Deployment, we scan for matching containers by name. So
    # it's possible that a Deployment matches a selector, but does not
    # have a container that matches. This is expected behavior, and moves
    # along gracefully. This allows a wider selector, and refine it by only
    # updating containers that match.

    # When a container is found within a Deployment, we patch the `image`.
    # This is roughly equivalent to doing `kubectl set image ...`. We also
    # patch in metadata about the deploy itself in the annotations on both
    # the Deployment and the PodTemplate. This decision was made so that
    # a bump of the annotations would cause a rolling restart of the service,
    # even if the image doesn't change. This means a re-deploy of a service
    # is not entirely a no-op, but will restart all Deployments still.
    for deployment in api.list_namespaced_deployment(**selector).items:
        namespace = deployment.metadata.name
        name = deployment.metadata.name
        changes = False
        for container in deployment.spec.template.spec.containers:
            for c in containers:
                if container.name == c["name"]:
                    container.image = c["image"]
                    changes = True

        # If there are any changes at all in this deployment, we need
        # to patch in our freight annotations, and trigger the PATCH call,
        # as well as set up the watcher to keep track of its rollout.
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
    # Execute a shell command within our workspace
    command = format_task(step["command"], context.task)
    context.workspace.run(command, env=step.get("env"))


def format_task(data, task: TaskContext):
    # Recursively formatting strings that may
    # contain taskcontext vars.
    if isinstance(data, str):
        return data.format(**asdict(task))
    if isinstance(data, list):
        return [format_task(d, task) for d in data]
    if isinstance(data, dict):
        return {k: format_task(v, task) for k, v in data.items()}
    return data


def make_job_spec(step: dict, task: TaskContext) -> dict:
    # Translate our customer KubernetesJob, which is just a subset of
    # allowed Kubernetes Job configs, into a real Job spec. This subset is
    # done so that we can control better what a Job means, including an
    # auto generated name, and enforcing the use of a single container.
    # The properties allowed to be defined are:
    #   name*, namespace, image*, args, env, volumeMounts, resources, volumes
    # * = required
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
    # Run a one-off Job in Kubernetes and track it through to completion.
    # Running a job in Kubernetes is a bit non-trivial, and involves the
    # following:
    #  * Create the Job spec
    #  * Querying for the Pod created by the Job until it is in a state
    #    other than Pending. This involves using the label: `job-name={jobname}`
    #  * Once we're past Pending, the Pod is either in Running, Succeeded,
    #    or Failed state. At this point, we read it's container logs until
    #    the pod exits.
    #  * Once the Pod exits, and we have fully read the logs, we are safe
    #    to proceed with reporting the step as success or failure.
    #  * When all said and done, we delete the Job, with it's children Pods
    #    to avoid these collecting and hanging around. It's still possible
    #    a Job may get orphaned, but these will eventually get cleaned up by
    #    Kubernetes, so it's not a huge deal if this happens.
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
        # Find our Pod that is spawned from this Job
        pods = (
            client.CoreV1Api(context.kube.client)
            .list_namespaced_pod(namespace=namespace, label_selector=f"job-name={name}")
            .items
        )
        assert len(pods) == 1, len(pods)
        pod_name = pods[0].metadata.name
        context.workspace.log.info(f"Waiting for Pod {pod_name}")

        # Now we begin our loop and shitty state machine
        read_logs = False
        while True:
            pod = client.CoreV1Api(context.kube.client).read_namespaced_pod(
                namespace=namespace, name=pod_name
            )
            # If we have successfully read our logs, we're ready to report
            # status.
            if read_logs:
                if pod.status.phase == "Failed":
                    raise StepFailed("Failed")
                return

            if pod.status.phase == "Pending":
                # If we are in a Pending state, we need to also check
                # if we're in the ContainerCreating phase of the container inside.
                # For any other event, like, an ErrImagePull, the Pod will
                # forever be left in Pending, but the container inside has errored.
                # So the only valid state to continue waiting is ContainerCreating.
                # Any other state is considered a failure.
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
                # At this point, our Pod has either begun running or finished.
                # For any case, we want to begin to tail (follow) logs until the
                # Pod exits. This works for both a running Pod, and a finished Pod
                # the same.

                # HACK: When _preload_context is passed, this causes the kubernetes
                # API here to return a urllib3 HTTPResponse object directly ready
                # to be streamed, so the following use of `resp.stream()` and
                # `resp.release_conn()` are just standard urllib3 behaviors.
                # This is entirely undocumented behavior afaik, and the only way to
                # actually get `follow=True` to work.
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
                # When finished reading logs, we need to loop back around
                # so we can query the final state of the Pod, in the case that
                # it was Running when we got here, we don't know if it succeeded
                # or failed.
    finally:
        context.workspace.log.info(f"Deleting Job {namespace}/{name}")
        client.BatchV1Api(context.kube.client).delete_namespaced_job(
            namespace=namespace, name=name, propagation_policy="Foreground"
        )


def rollout_status_deployment(
    api: client.AppsV1beta1Api, name: str, namespace: str, generation: int
) -> Tuple[str, bool]:
    # tbh this is mostly ported from Go into Python from:
    # https://github.com/kubernetes/kubernetes/blob/master/pkg/kubectl/rollout_status.go#L76-L92
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

from kubernetes import client

from src.main.mlpad.notebook.storage import get_pvc_name


def get_target_port(image: str) -> int:
    if image == "code-server":
        return 8443
    return -1


def get_supported_images():
    return ["code-server"]


def get_notebook_deployment_name(notebook_name: str) -> str:
    """
    Returns the deployment name for the given notebook name.
    The deployment name is constructed by appending '-deploy' to the notebook name.
    """
    return f"{notebook_name}-deploy"


def is_notebook_exists(namespace: str, name: str) -> bool:
    try:
        client.CustomObjectsApi().get_namespaced_custom_object(
            group="mlpad.venkateswarluvajrala.com",
            version="v1",
            namespace=namespace,
            name=name,
            plural="notebooks",
        )
        return True
    except client.ApiException as e:
        if e.status == 404:
            return False
        raise e


def get_notebook_uid(namespace, notebook_name) -> str:
    if not is_notebook_exists(namespace, notebook_name):
        raise Exception(
            f"Notebook {notebook_name} does not exist in namespace {namespace}"
        )

    notebook = client.CustomObjectsApi().get_namespaced_custom_object(
        group="mlpad.venkateswarluvajrala.com",
        version="v1",
        namespace=namespace,
        name=notebook_name,
        plural="notebooks",
    )

    print("Notebook details:", notebook)
    return notebook.get("metadata").get("uid")


def code_server_config(
    container_name: str, container_size: str, volume_mounts: list[client.V1VolumeMount]
) -> client.V1Container:
    resources = get_resources(container_size)
    return client.V1Container(
        name=container_name,
        image="lscr.io/linuxserver/code-server:latest",
        ports=[client.V1ContainerPort(container_port=8443)],
        env=[
            client.V1EnvVar(name="TZ", value="Etc/UTC"),
            client.V1EnvVar(name="DEFAULT_WORKSPACE", value="/workspace"),
            client.V1EnvVar(name="PWA_APPNAME", value="code-server"),
            client.V1EnvVar(name="CS_DISABLE_GETTING_STARTED_OVERRIDE", value="true"),
            client.V1EnvVar(name="DISABLE_TELEMETRY", value="true"),
        ],
        resources=resources,
        volume_mounts=volume_mounts,
    )


def get_resources(container_size):
    if container_size == "medium":
        resources = client.V1ResourceRequirements(limits={"cpu": "1", "memory": "1Gi"})
    elif container_size == "large":
        resources = client.V1ResourceRequirements(limits={"cpu": "2", "memory": "2Gi"})
    else:
        resources = client.V1ResourceRequirements(
            limits={"cpu": "500m", "memory": "512Mi"}
        )
    return resources


def get_notebook_pod_template(
    notebook_name: str, image: str, container_size: str, labels: dict[str, str]
) -> client.V1PodTemplateSpec:
    volumes = [
        client.V1Volume(
            name="storage-volume",
            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                claim_name=get_pvc_name(notebook_name)
            ),
        )
    ]
    if image == "code-server":
        return client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={**labels, "image": "code-server"}),
            spec=client.V1PodSpec(
                containers=[
                    code_server_config(
                        container_name=image,
                        container_size=container_size,
                        volume_mounts=[
                            client.V1VolumeMount(
                                mount_path="/config",
                                name="storage-volume",
                                sub_path="config",
                            ),
                            client.V1VolumeMount(
                                mount_path="/workspace",
                                name="storage-volume",
                                sub_path="workspace",
                            ),
                        ],
                    )
                ],
                volumes=volumes,
            ),
        )
    raise Exception(
        f"Unsupported image type. Supported images: {get_supported_images()}"
    )


def create_notebook_deploy(
    default_labels: dict[str, str],
    image: str,
    namespace: str,
    notebook_name: str,
    container_size: str,
) -> None:
    deploy_name = get_notebook_deployment_name(notebook_name=notebook_name)
    pod_labels = {"name": notebook_name, **default_labels}
    notebook_uid = get_notebook_uid(namespace, notebook_name)
    notebook_pod_template = get_notebook_pod_template(
        image=image,
        notebook_name=notebook_name,
        container_size=container_size,
        labels=pod_labels,
    )

    body = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(
            name=deploy_name,
            owner_references=[
                client.V1OwnerReference(
                    api_version="mlpad.venkateswarluvajrala.com/v1",
                    name=notebook_name,
                    uid=notebook_uid,
                    kind="Notebook",
                )
            ],
            namespace=namespace,
            labels={**default_labels, "name": deploy_name},
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels=pod_labels),
            template=notebook_pod_template,
        ),
    )

    client.AppsV1Api().create_namespaced_deployment(namespace=namespace, body=body)

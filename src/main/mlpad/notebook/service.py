import logging

from kubernetes import client

from src.main.mlpad.notebook.deployment import (
    get_notebook_deployment_name,
    get_notebook_uid,
    get_target_port,
    get_supported_images,
)


def get_service_name(notebook_name: str) -> str:
    return f"{notebook_name}-svc"


def is_notebook_service_exists(name: str, namespace: str) -> bool:
    try:
        client.CoreV1Api().read_namespaced_service(name=name, namespace=namespace)
        return True
    except client.ApiException as e:
        if e.status == 404:
            return False
        raise e


def create_service(
        name: str,
        namespace: str,
        selector_labels: dict[str, str],
        target_port: int,
        owner_references: list[client.V1OwnerReference],
        port: int = 80,
        protocol: str = "TCP",
) -> None:
    api_instance = client.CoreV1Api()
    namespace = namespace

    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name=name, namespace=namespace, owner_references=owner_references
        ),
        spec=client.V1ServiceSpec(
            selector=selector_labels,
            ports=[
                client.V1ServicePort(
                    port=port, target_port=target_port, protocol=protocol
                )
            ],
            type="NodePort",
        ),
    )

    api_instance.create_namespaced_service(namespace=namespace, body=service)


def create_notebook_service(
        notebook_name: str, default_labels: dict[str, str], image: str, namespace: str
) -> None:
    selector_labels = {
        **default_labels,
        "name": notebook_name,
    }

    service_name = get_service_name(notebook_name=notebook_name)

    if is_notebook_service_exists(name=service_name, namespace=namespace):
        logging.info(
            f"Service with name {service_name} already exists in namespace {namespace}. Skipping creation."
        )
        return

    target_port = get_target_port(image=image)
    notebook_uid = get_notebook_uid(namespace=namespace, notebook_name=notebook_name)

    owner_references = [
        client.V1OwnerReference(
            api_version="mlpad.venkateswarluvajrala.com/v1",
            name=notebook_name,
            uid=notebook_uid,
            kind="Notebook",
        )
    ]
    if target_port == -1:
        logging.error(
            f"Unsupported image type: {image}. Supported images: {get_supported_images()}"
        )
        return
    create_service(
        name=service_name,
        namespace=namespace,
        selector_labels=selector_labels,
        target_port=target_port,
        owner_references=owner_references,
    )


def update_notebook_endpoint(name: str, namespace: str):
    api_instance = client.CoreV1Api()
    service_name = get_service_name(notebook_name=name)
    try:
        service = api_instance.read_namespaced_service(name=service_name, namespace=namespace)
        endpoint = f"http://{service.spec.cluster_ip}:{service.spec.ports[0].node_port}"
        custom_object_api_instance = client.CustomObjectsApi()
        object_meta = {
            "metadata": client.V1ObjectMeta(
                annotations={"endpoint": endpoint},
                namespace=namespace
            )
        }
        custom_object_api_instance.patch_namespaced_custom_object(
            group="mlpad.venkateswarluvajrala.com",
            version="v1",
            namespace="mlpad",
            plural="notebooks",
            body=object_meta,
            name=name,
        )

    except client.ApiException as e:
        logging.error(f"Failed to update endpoint for notebook {name}: {e}")

import logging

from kubernetes import client


def get_pvc_name(notebook_name: str) -> str:
    """
    Generate the Persistent Volume Claim (PVC) name based on the notebook name.
    """
    return f"{notebook_name}-pvc"


def is_persistent_volume_claim_exists(name: str, namespace: str) -> bool:
    try:
        client.CoreV1Api().read_namespaced_persistent_volume_claim(
            name=name, namespace=namespace
        )
        return True
    except client.ApiException as e:
        if e.status == 404:
            return False
        raise e


def create_pvc(default_labels, notebook_name, namespace, storage) -> None:
    pvc_name = get_pvc_name(notebook_name)
    pvc_data = client.V1PersistentVolumeClaim(
        api_version="v1",
        kind="PersistentVolumeClaim",
        metadata=client.V1ObjectMeta(
            name=pvc_name,
            namespace=namespace,
            labels={**default_labels, "name": pvc_name},
        ),
        spec=client.V1PersistentVolumeClaimSpec(
            storage_class_name="local-path",
            access_modes=["ReadWriteOnce"],
            resources=client.V1VolumeResourceRequirements(
                requests={"storage": f"{storage}Gi"}
            ),
        ),
    )

    client.CoreV1Api().create_namespaced_persistent_volume_claim(
        namespace=namespace, body=pvc_data
    )


def create_storage(default_labels, notebook_name, namespace, storage) -> None:
    pvc_name = get_pvc_name(notebook_name)
    if is_persistent_volume_claim_exists(name=pvc_name, namespace=namespace):
        logging.info(
            f"Existing Persistent Volume Claim with name {pvc_name} found, skipping PVC creation."
        )
        return
    create_pvc(
        default_labels=default_labels,
        notebook_name=notebook_name,
        namespace=namespace,
        storage=storage,
    )


def add_storage_suffix(default_labels, notebook_name, namespace, storage) -> None:
    custom_object_api_instance = client.CustomObjectsApi()
    object_meta = {
        "metadata": client.V1ObjectMeta(
            annotations={"storageReadable": f"{storage}Gi"},
            namespace=namespace,
            labels=default_labels,
        )
    }
    custom_object_api_instance.patch_namespaced_custom_object(
        group="mlpad.venkateswarluvajrala.com",
        version="v1",
        namespace="mlpad",
        plural="notebooks",
        body=object_meta,
        name=notebook_name,
    )

import kopf
import logging
from kubernetes import client


@kopf.on.create(
    kind="Notebook", group="mlpad.venkateswarluvajrala.com", retries=3, backoff=30
)
def create_notebook(name: str, spec: kopf.Spec, namespace: str, **kwargs):
    api_instance = client.CustomObjectsApi()
    storage = spec["storageSize"]
    object_meta = {
        "metadata": client.V1ObjectMeta(
            annotations={"storageReadable": f"{storage}Gi"}, namespace=namespace
        )
    }
    api_instance.patch_namespaced_custom_object(
        group="mlpad.venkateswarluvajrala.com",
        version="v1",
        namespace="mlpad",
        plural="notebooks",
        body=object_meta,
        name=name,
    )

    logging.info(f"Patch is success with name: {name} body: {object_meta}")

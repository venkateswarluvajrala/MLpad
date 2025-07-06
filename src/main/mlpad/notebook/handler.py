import kopf
import logging

from src.main.mlpad.notebook.deployment import create_notebook_deploy
from src.main.mlpad.notebook.storage import add_storage_suffix, create_storage
from src.main.mlpad.notebook.service import create_notebook_service
from src.main.mlpad.notebook.service import update_notebook_endpoint


@kopf.on.create(
    kind="Notebook", group="mlpad.venkateswarluvajrala.com", retries=3, backoff=30
)
def create_notebook(name: str, spec: kopf.Spec, namespace: str, **kwargs):
    default_labels = {
        "app": "mlpad",
        "component": "notebook",
        "managed-by": "mlpad-operator",
    }
    storage = spec["storageSize"]
    image = spec["image"]

    add_storage_suffix(
        default_labels=default_labels,
        notebook_name=name,
        namespace=namespace,
        storage=storage,
    )
    create_storage(
        default_labels=default_labels,
        notebook_name=name,
        namespace=namespace,
        storage=storage,
    )
    create_notebook_deploy(
        default_labels=default_labels,
        image=image,
        namespace=namespace,
        notebook_name=name,
        container_size=spec["containerSize"],
    )

    create_notebook_service(
        notebook_name=name,
        namespace=namespace,
        image=image,
        default_labels=default_labels,
    )

    update_notebook_endpoint(name=name, namespace=namespace)

    logging.info(
        f"Notebook {name} created with storage size {storage}Gi in namespace {namespace}."
    )

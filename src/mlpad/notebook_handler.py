import kopf
import logging


@kopf.on.create(kind='Notebook', retries=3, backoff=30)
def create_notebook(name: str, spec: kopf.Spec, meta: kopf.Meta, status: kopf.Status, namespace: str, **kwargs):
    logging.info(f"Notebook created with spec: {spec}! name: {name} metadata: {meta} status: {status}")

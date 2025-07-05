from typing import cast
from unittest.mock import patch, MagicMock
import kopf
import kubernetes.client
import pytest

from src.main.mlpad.notebook.handler import create_notebook


@pytest.fixture()
def notebook_spec():
    storage_size = 10
    spec = cast(
        kopf.Spec,
        {
            "storageSize": 10,
            "image": "code-server",
            "containerSize": "small",
        },
    )
    data = {
        "name": "valid-notebook",
        "namespace": "mlpad",
        "storage_size": storage_size,
        "spec": spec,
    }
    return data


class TestNotebook:
    def test_should_create_new_notebook_with_valid_values(self, notebook_spec):
        name = notebook_spec.get("name")
        namespace = notebook_spec.get("namespace")
        storage_size = notebook_spec.get("storage_size")
        object_meta = {
            "metadata": kubernetes.client.V1ObjectMeta(
                annotations={"storageReadable": f"{storage_size}Gi"},
                namespace=namespace,
            )
        }

        with patch(
                "src.main.mlpad.notebook.handler.client.CustomObjectsApi"
        ) as mock_custom_objects_api:
            mock_kubernetes_client = MagicMock()
            mock_custom_objects_api.return_value = mock_kubernetes_client
            mock_kubernetes_client.patch_namespaced_custom_object.return_value = None

            create_notebook(
                name=name, namespace=namespace, spec=notebook_spec.get("spec")
            )

            mock_kubernetes_client.patch_namespaced_custom_object.assert_called_once_with(
                group="mlpad.venkateswarluvajrala.com",
                version="v1",
                namespace="mlpad",
                plural="notebooks",
                body=object_meta,
                name=name,
            )

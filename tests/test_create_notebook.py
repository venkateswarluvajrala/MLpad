from typing import cast
from unittest.mock import patch, MagicMock
import kopf
import kubernetes.client

from src.mlpad.notebook_handler import create_notebook


class TestNotebook:
    def test_should_create_new_notebook_with_valid_values(self):
        name = "valid-notebook"
        namespace = "mlpad"
        storage_size = 10
        spec = cast(
            kopf.Spec,
            {
                "storageSize": storage_size,
                "image": "code-server",
                "containerSize": "small",
            },
        )
        object_meta = {
            "metadata": kubernetes.client.V1ObjectMeta(
                annotations={"storageReadable": f"{storage_size}Gi"},
                namespace=namespace,
            )
        }

        with patch(
            "src.mlpad.notebook_handler.client.CustomObjectsApi"
        ) as mock_custom_objects_api:
            mock_kubernetes_client = MagicMock()
            mock_custom_objects_api.return_value = mock_kubernetes_client
            mock_kubernetes_client.patch_namespaced_custom_object.return_value = None

            create_notebook(name=name, namespace=namespace, spec=spec)

            mock_kubernetes_client.patch_namespaced_custom_object.assert_called_once_with(
                group="mlpad.venkateswarluvajrala.com",
                version="v1",
                namespace="mlpad",
                plural="notebooks",
                body=object_meta,
                name=name,
            )

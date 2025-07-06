from typing import cast
from unittest.mock import patch
import kopf
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
        with patch(
            "src.main.mlpad.notebook.handler.create_notebook_deploy"
        ) as mock_create_deploy:
            with patch(
                "src.main.mlpad.notebook.handler.create_storage"
            ) as mock_create_storage:
                with patch(
                    "src.main.mlpad.notebook.handler.add_storage_suffix"
                ) as mock_add_suffix:
                    with patch(
                            "src.main.mlpad.notebook.handler.create_notebook_service"
                    ) as mock_create_Service:
                        with patch(
                                "src.main.mlpad.notebook.handler.update_notebook_endpoint"
                        ) as mock_update_notebook_endpoint:
                            create_notebook(
                                name=notebook_spec["name"],
                                spec=notebook_spec["spec"],
                                namespace=notebook_spec["namespace"],
                            )
                            mock_add_suffix.assert_called_once_with(
                                default_labels={
                                    "app": "mlpad",
                                    "component": "notebook",
                                    "managed-by": "mlpad-operator",
                                },
                                notebook_name=notebook_spec["name"],
                                namespace=notebook_spec["namespace"],
                                storage=notebook_spec["storage_size"],
                            )
                            mock_create_storage.assert_called_once_with(
                                default_labels={
                                    "app": "mlpad",
                                    "component": "notebook",
                                    "managed-by": "mlpad-operator",
                                },
                                notebook_name=notebook_spec["name"],
                                namespace=notebook_spec["namespace"],
                                storage=notebook_spec["storage_size"],
                            )
                            mock_create_deploy.assert_called_once_with(
                                default_labels={
                                    "app": "mlpad",
                                    "component": "notebook",
                                    "managed-by": "mlpad-operator",
                                },
                                image=notebook_spec["spec"]["image"],
                                namespace=notebook_spec["namespace"],
                                notebook_name=notebook_spec["name"],
                                container_size=notebook_spec["spec"]["containerSize"],
                            )

                            mock_create_Service.assert_called_once_with(notebook_name=notebook_spec["name"],
                                                                        namespace=notebook_spec["namespace"],
                                                                        image=notebook_spec["spec"]["image"],
                                                                        default_labels={
                                                                            "app": "mlpad",
                                                                            "component": "notebook",
                                                                            "managed-by": "mlpad-operator",
                                                                        })
                            mock_update_notebook_endpoint.assert_called_once_with(name=notebook_spec["name"],namespace=notebook_spec["namespace"])

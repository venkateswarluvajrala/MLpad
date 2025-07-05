import pytest
from src.main.mlpad.notebook.deployment import create_notebook_deploy
from unittest.mock import patch


class TestDeploy:

    def test_should_throw_error_if_notebook_deploy_doesnt_exist_when_getting_notebook_uid(self):
        from src.main.mlpad.notebook.deployment import get_notebook_uid

        with pytest.raises(Exception) as e:
            get_notebook_uid("default", "non-existent-notebook")
            assert e.value == "Notebook non-existent-notebook does not exist in namespace default"

    def test_should_return_notebook_uid_when_notebook_deploy_exists(self):
        from src.main.mlpad.notebook.deployment import get_notebook_uid
        from unittest.mock import patch

        with patch("src.main.mlpad.notebook.deployment.client.CustomObjectsApi") as mock_api:
            mock_api.return_value.get_namespaced_custom_object.return_value = {
                "metadata": {"uid": "12345"}
            }
            uid = get_notebook_uid("default", "existing-notebook")
            assert uid == "12345"

    def test_create_notebook_deploy_should_deploy_notebook_with_correct_labels(self):
        default_labels = {
            "app": "mlpad",
            "component": "notebook",
            "managed-by": "mlpad-operator",
        }
        with patch("src.main.mlpad.notebook.deployment.client.AppsV1Api") as mock_api:
            with patch("src.main.mlpad.notebook.deployment.client.AppsV1Api.create_namespaced_deployment") as mock_create:
                with patch("src.main.mlpad.notebook.deployment.get_notebook_uid") as mock_get_uid:
                    mock_get_uid.return_value = "12345"
                    mock_api.return_value.create_namespaced_deployment = mock_create
                    create_notebook_deploy(
                        default_labels=default_labels,
                        image="code-server",
                        namespace="mlpad",
                        notebook_name="test-notebook",
                        container_size="medium"
                    )
                    mock_api.return_value.create_namespaced_deployment.assert_called_once()
                    deployment_args = mock_api.return_value.create_namespaced_deployment.call_args[1]
                    mock_api.create_namespaced_deployment.assert_called_once_with(
                        namespace="mlpad",
                        body=deployment_args["body"]
                    )



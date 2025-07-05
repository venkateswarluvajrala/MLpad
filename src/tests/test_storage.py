from src.main.mlpad.notebook.storage import create_storage, create_pvc
from unittest.mock import patch, MagicMock
from src.main.mlpad.notebook.storage import add_storage_suffix
from kubernetes import client


class TestStorage:
    def test_should_skip_storage_creation_if_storage_already_exist(self):
        notebook_name = "test-notebook"
        namespace = "test-namespace"
        storage = 10
        default_labels = {"app": "mlpad"}

        with patch(
            "src.main.mlpad.notebook.storage.is_persistent_volume_claim_exists"
        ) as mock_is_pvc_exists:
            mock_is_pvc_exists.return_value = True

            with patch("src.main.mlpad.notebook.storage.create_pvc") as mock_create_pvc:
                create_storage(default_labels, notebook_name, namespace, storage)

                mock_create_pvc.assert_not_called()
                mock_is_pvc_exists.assert_called_once_with(
                    name=f"{notebook_name}-pvc", namespace=namespace
                )

    def test_should_create_storage_if_not_exists(self):
        notebook_name = "test-notebook"
        namespace = "test-namespace"
        storage = 10
        default_labels = {"app": "mlpad"}

        with patch(
            "src.main.mlpad.notebook.storage.is_persistent_volume_claim_exists"
        ) as mock_is_pvc_exists:
            mock_is_pvc_exists.return_value = False

            with patch("src.main.mlpad.notebook.storage.create_pvc") as mock_create_pvc:
                create_storage(default_labels, notebook_name, namespace, storage)

                mock_is_pvc_exists.assert_called_once_with(
                    name=f"{notebook_name}-pvc", namespace=namespace
                )
                mock_create_pvc.assert_called_once_with(
                    default_labels=default_labels,
                    notebook_name=notebook_name,
                    namespace=namespace,
                    storage=storage,
                )

    def test_should_add_storage_suffix(self):
        notebook_name = "test-notebook"
        namespace = "mlpad"
        storage = 10
        default_labels = {"app": "mlpad"}
        object_meta = {
            "metadata": client.V1ObjectMeta(
                annotations={"storageReadable": f"{storage}Gi"},
                namespace=namespace,
                labels=default_labels,
            )
        }

        with patch(
            "src.main.mlpad.notebook.storage.client.CustomObjectsApi"
        ) as mock_custom_objects_api:
            mock_api_instance = MagicMock()
            mock_custom_objects_api.return_value = mock_api_instance

            add_storage_suffix(default_labels, notebook_name, namespace, storage)

            mock_api_instance.patch_namespaced_custom_object.assert_called_once_with(
                group="mlpad.venkateswarluvajrala.com",
                version="v1",
                namespace=namespace,
                plural="notebooks",
                body=object_meta,
                name=notebook_name,
            )

    # I wish to test create_pvc function not create_storage function
    def test_should_create_pvc_with_given_values(self):
        notebook_name = "test-notebook"
        namespace = "test-namespace"
        storage = 10
        default_labels = {"app": "mlpad"}
        pvc_name = f"{notebook_name}-pvc"

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

        with patch(
            "src.main.mlpad.notebook.storage.client.CoreV1Api"
        ) as mock_core_v1_api:
            mock_api_instance = MagicMock()
            mock_core_v1_api.return_value = mock_api_instance

            create_pvc(
                default_labels=default_labels,
                notebook_name=notebook_name,
                namespace=namespace,
                storage=storage,
            )

            mock_api_instance.create_namespaced_persistent_volume_claim.assert_called_once_with(
                namespace=namespace, body=pvc_data
            )

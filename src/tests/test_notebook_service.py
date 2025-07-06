class TestNotebookService:
    def test_should_skip_service_creation_if_already_exists(self):
        from src.main.mlpad.notebook.service import create_notebook_service
        from unittest.mock import patch

        with patch(
                "src.main.mlpad.notebook.service.is_notebook_service_exists"
        ) as mock_exists:
            with patch("src.main.mlpad.notebook.service.get_notebook_uid") as mock_notebook_uid:
                with patch("src.main.mlpad.notebook.service.create_service") as mock_service:

                    mock_exists.return_value = True
                    mock_notebook_uid.return_value = "1234"
                    create_notebook_service(
                        notebook_name="test-notebook",
                        default_labels={"app": "mlpad"},
                        image="code-server",
                        namespace="mlpad",
                    )
                    mock_exists.assert_called_once_with(
                        name="test-notebook-svc", namespace="mlpad"
                    )
                    mock_service.assert_not_called()



    def test_should_create_service_when_notebook_service_does_not_exist(self):
        from src.main.mlpad.notebook.service import create_notebook_service
        from unittest.mock import patch

        with patch(
                "src.main.mlpad.notebook.service.is_notebook_service_exists"
        ) as mock_exists:
            with patch("src.main.mlpad.notebook.service.get_notebook_uid") as mock_notebook_uid:
                with patch("src.main.mlpad.notebook.service.create_service") as mock_service:

                    mock_exists.return_value = False
                    mock_notebook_uid.return_value = "1234"
                    create_notebook_service(
                        notebook_name="test-notebook",
                        default_labels={"app": "mlpad"},
                        image="code-server",
                        namespace="mlpad",
                    )
                    mock_exists.assert_called_once_with(
                        name="test-notebook-svc", namespace="mlpad"
                    )
                    mock_service.assert_called_once()
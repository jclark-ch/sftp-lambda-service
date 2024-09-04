import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from src.secrets_manager import get_secret

class TestSecretsManager(unittest.TestCase):
    """
    Test suite for the Secrets Manager utility function.

    This class contains unit tests for the get_secret function, which
    retrieves secrets from AWS Secrets Manager.
    """

    @patch('boto3.session.Session')
    def test_get_secret_string(self, mock_session):
        """
        Test retrieving a string secret from Secrets Manager.

        This test verifies that get_secret correctly retrieves and returns
        a string secret from AWS Secrets Manager.

        Args:
            mock_session (MagicMock): Mocked boto3 session
        """
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': 'test-secret-value'
        }

        result = get_secret('test-secret-name')

        self.assertEqual(result, 'test-secret-value')
        mock_client.get_secret_value.assert_called_once_with(SecretId='test-secret-name')

    @patch('boto3.session.Session')
    def test_get_secret_binary(self, mock_session):
        """
        Test retrieving a binary secret from Secrets Manager.

        This test verifies that get_secret correctly retrieves and returns
        a binary secret from AWS Secrets Manager.

        Args:
            mock_session (MagicMock): Mocked boto3 session
        """
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretBinary': b'test-binary-secret'
        }

        result = get_secret('test-secret-name')

        self.assertEqual(result, b'test-binary-secret')
        mock_client.get_secret_value.assert_called_once_with(SecretId='test-secret-name')

    @patch('boto3.session.Session')
    def test_get_secret_error(self, mock_session):
        """
        Test error handling when retrieving a secret fails.

        This test verifies that get_secret correctly handles and raises
        exceptions when AWS Secrets Manager encounters an error.

        Args:
            mock_session (MagicMock): Mocked boto3 session
        """
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Secret not found'}},
            'GetSecretValue'
        )

        with self.assertRaises(ClientError):
            get_secret('non-existent-secret')

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

from src.lambda_function import lambda_handler, create_temporary_server, create_user, update_user_policy

class TestLambdaFunction(unittest.TestCase):
    """
    Test suite for the SFTP Lambda function.

    This class contains unit tests for the main Lambda function and its
    helper functions. It uses mocking to simulate AWS service interactions.
    """

    def setUp(self):
        """
        Set up method to initialize common test variables and mocks.

        This method is run before each test method.
        """
        self.mock_transfer = MagicMock()
        self.mock_s3 = MagicMock()
        self.test_event = {
            'customer_id': 'test-customer-001',
            'ssh_public_key': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...',
            'allowed_ips': ['203.0.113.0/24'],
            'lifetime_minutes': 5
        }

    @patch('src.lambda_function.boto3.client')
    def test_lambda_handler_success(self, mock_boto3_client):
        """
        Test the lambda_handler function for a successful execution.

        This test verifies that the lambda_handler correctly processes
        a valid input event and returns the expected response.

        Args:
            mock_boto3_client (MagicMock): Mocked boto3 client
        """
        mock_boto3_client.side_effect = [self.mock_transfer, self.mock_s3]
        self.mock_transfer.create_server.return_value = {'ServerId': 'test-server-id'}
        
        response = lambda_handler(self.test_event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertIn('sftp_hostname', body)
        self.assertIn('sftp_username', body)
        self.assertEqual(body['customer_id'], 'test-customer-001')

    @patch('src.lambda_function.boto3.client')
    def test_lambda_handler_error(self, mock_boto3_client):
        """
        Test the lambda_handler function for error handling.

        This test verifies that the lambda_handler correctly handles
        and reports errors when an exception occurs during execution.

        Args:
            mock_boto3_client (MagicMock): Mocked boto3 client
        """
        mock_boto3_client.side_effect = Exception("Test error")
        
        response = lambda_handler(self.test_event, None)
        
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)

    def test_create_temporary_server(self):
        """
        Test the create_temporary_server function.

        This test verifies that create_temporary_server correctly calls
        the AWS Transfer create_server method with the right parameters.
        """
        self.mock_transfer.create_server.return_value = {'ServerId': 'test-server-id'}
        
        server_id = create_temporary_server(self.mock_transfer, 'test-customer-001', 5)
        
        self.assertEqual(server_id, 'test-server-id')
        self.mock_transfer.create_server.assert_called_once()
        call_args = self.mock_transfer.create_server.call_args[1]
        self.assertEqual(call_args['Protocols'], ['SFTP'])
        self.assertIn({'Key': 'CustomerId', 'Value': 'test-customer-001'}, call_args['Tags'])

    def test_create_user(self):
        """
        Test the create_user function.

        This test verifies that create_user correctly calls the AWS Transfer
        create_user method with the right parameters and handles the
        optional SSH key and IP restrictions.
        """
        user_name = create_user(self.mock_transfer, 'test-server-id', 'test-customer-001', 
                                'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...', ['203.0.113.0/24'])
        
        self.assertEqual(user_name, 'temp-user-test-customer-001')
        self.mock_transfer.create_user.assert_called_once()
        call_args = self.mock_transfer.create_user.call_args[1]
        self.assertEqual(call_args['ServerId'], 'test-server-id')
        self.assertEqual(call_args['UserName'], 'temp-user-test-customer-001')
        self.assertIn('SshPublicKeys', call_args)

    def test_update_user_policy(self):
        """
        Test the update_user_policy function.

        This test verifies that update_user_policy correctly calls the
        AWS Transfer update_access method with the right policy containing
        the specified IP restrictions.
        """
        update_user_policy(self.mock_transfer, 'test-server-id', 'test-user', 'test-customer-001', ['203.0.113.0/24'])
        
        self.mock_transfer.update_access.assert_called_once()
        call_args = self.mock_transfer.update_access.call_args[1]
        self.assertEqual(call_args['ServerId'], 'test-server-id')
        policy = json.loads(call_args['Policy'])
        self.assertIn('IpAddress', policy['Statement'][0]['Condition'])
        self.assertEqual(policy['Statement'][0]['Condition']['IpAddress']['aws:SourceIp'], ['203.0.113.0/24'])

if __name__ == '__main__':
    unittest.main()
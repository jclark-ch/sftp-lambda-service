import boto3
import json
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main handler for the Lambda function.

    This function processes incoming requests to create temporary SFTP servers
    and users. It manages the creation of servers, users, and sets up appropriate
    access policies based on the provided parameters.

    Args:
        event (dict): The event dict containing input parameters:
            - customer_id (str): Unique identifier for the customer
            - ssh_public_key (str, optional): SSH public key for user authentication
            - allowed_ips (list, optional): List of allowed IP addresses or CIDR blocks
            - lifetime_minutes (int, optional): Lifetime of the SFTP server in minutes (default: 5)
        context (object): Lambda context object

    Returns:
        dict: A dictionary containing:
            - statusCode (int): HTTP status code
            - body (str): JSON string with server details or error message
    
    Raises:
        Exception: Any unexpected errors during execution
    """
    logger.info(f"Lambda function invoked with event: {json.dumps(event)}")
    
    transfer = boto3.client('transfer')
    s3 = boto3.client('s3')
    
    try:
        customer_id = event['customer_id']
        ssh_public_key = event.get('ssh_public_key')
        allowed_ips = event.get('allowed_ips')
        lifetime_minutes = event.get('lifetime_minutes', 5)  # Default to 5 minutes if not specified
        
        logger.info(f"Processing request for customer_id: {customer_id} with lifetime: {lifetime_minutes} minutes")
        
        server_id = create_temporary_server(transfer, customer_id, lifetime_minutes)
        user_name = create_user(transfer, server_id, customer_id, ssh_public_key, allowed_ips)
        
        sftp_hostname = f"{server_id}.server.transfer.{os.environ['AWS_REGION']}.amazonaws.com"
        expiration_time = datetime.utcnow() + timedelta(minutes=lifetime_minutes)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Temporary SFTP server created for {lifetime_minutes} minutes',
                'sftp_hostname': sftp_hostname,
                'sftp_username': user_name,
                'customer_id': customer_id,
                'expiration_time': expiration_time.isoformat()
            })
        }
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred while processing your request',
                'error': str(e)
            })
        }

def create_temporary_server(transfer, customer_id, lifetime_minutes):
    """
    Creates a temporary SFTP server for the specified customer.

    This function sets up a new SFTP server using AWS Transfer Family, 
    configures it with the appropriate settings, and tags it with 
    the customer ID and expiration time.

    Args:
        transfer (boto3.client): Boto3 Transfer Family client
        customer_id (str): Unique identifier for the customer
        lifetime_minutes (int): Lifetime of the server in minutes

    Returns:
        str: The ID of the newly created server

    Raises:
        ClientError: If there's an issue with the AWS API call
    """
    logger.info(f"Creating temporary server for customer {customer_id}")
    response = transfer.create_server(
        EndpointType='PUBLIC',
        IdentityProviderType='SERVICE_MANAGED',
        LoggingRole='arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_LOGGING_ROLE',
        Protocols=['SFTP'],
        SecurityPolicyName='TransferSecurityPolicy-2022-03',
        Tags=[
            {'Key': 'CustomerId', 'Value': customer_id},
            {'Key': 'ExpirationTime', 'Value': (datetime.utcnow() + timedelta(minutes=lifetime_minutes)).isoformat()}
        ]
    )
    server_id = response['ServerId']
    logger.info(f"Created temporary server: {server_id}")
    return server_id

def create_user(transfer, server_id, customer_id, ssh_public_key, allowed_ips):
    """
    Creates a new user for the specified SFTP server.

    This function sets up a new user on the given SFTP server, configures
    their home directory, and optionally sets up SSH key authentication 
    and IP restrictions.

    Args:
        transfer (boto3.client): Boto3 Transfer Family client
        server_id (str): ID of the SFTP server
        customer_id (str): Unique identifier for the customer
        ssh_public_key (str, optional): SSH public key for user authentication
        allowed_ips (list, optional): List of allowed IP addresses or CIDR blocks

    Returns:
        str: The username of the newly created user

    Raises:
        ClientError: If there's an issue with the AWS API call
    """
    user_name = f"temp-user-{customer_id}"
    logger.info(f"Creating user {user_name} for server {server_id}")
    user_params = {
        'ServerId': server_id,
        'UserName': user_name,
        'Role': 'arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_SFTP_USER_ROLE',
        'HomeDirectory': f"/YOUR_S3_BUCKET_NAME/{customer_id}"
    }
    if ssh_public_key:
        user_params['SshPublicKeys'] = [ssh_public_key]
    
    transfer.create_user(**user_params)
    logger.info(f"User {user_name} created successfully")
    
    if allowed_ips:
        update_user_policy(transfer, server_id, user_name, customer_id, allowed_ips)
    
    return user_name

def update_user_policy(transfer, server_id, user_name, customer_id, allowed_ips):
    """
    Updates the access policy for a user with IP restrictions.

    This function creates and applies an access policy to the specified user,
    restricting access to only the provided IP addresses or CIDR blocks.

    Args:
        transfer (boto3.client): Boto3 Transfer Family client
        server_id (str): ID of the SFTP server
        user_name (str): Username of the SFTP user
        customer_id (str): Unique identifier for the customer
        allowed_ips (list): List of allowed IP addresses or CIDR blocks

    Raises:
        ClientError: If there's an issue with the AWS API call
    """
    logger.info(f"Updating policy for user {user_name} with IP restrictions: {allowed_ips}")
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "transfer:*",
                "Resource": "*",
                "Condition": {
                    "IpAddress": {
                        "aws:SourceIp": allowed_ips
                    }
                }
            }
        ]
    }
    transfer.update_access(
        ServerId=server_id,
        HomeDirectory=f"/YOUR_S3_BUCKET_NAME/{customer_id}",
        HomeDirectoryType='PATH',
        Policy=json.dumps(policy)
    )
    logger.info(f"Policy updated successfully for user {user_name}")
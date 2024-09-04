import boto3
import json
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main handler for the cleanup Lambda function.

    This function is responsible for identifying and deleting expired SFTP servers.
    It runs periodically to ensure that temporary servers are removed after their
    designated lifetime has elapsed.

    Args:
        event (dict): The event dict that triggers the Lambda function.
            This function doesn't use any specific event properties.
        context (object): Lambda context object

    Returns:
        dict: A dictionary containing:
            - statusCode (int): HTTP status code
            - body (str): JSON string with the cleanup result or error message
    
    Raises:
        Exception: Any unexpected errors during execution
    """
    logger.info(f"Cleanup Lambda function invoked with event: {json.dumps(event)}")
    
    transfer = boto3.client('transfer')
    
    try:
        deleted_servers = cleanup_expired_servers(transfer)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Cleanup completed successfully',
                'deleted_servers': deleted_servers
            })
        }
    
    except Exception as e:
        logger.error(f"An error occurred during cleanup: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred during cleanup',
                'error': str(e)
            })
        }

def cleanup_expired_servers(transfer):
    """
    Identifies and deletes expired SFTP servers.

    This function lists all SFTP servers, checks their expiration time,
    and deletes the servers that have expired. The expiration time is
    determined by the 'ExpirationTime' tag on each server.

    Args:
        transfer (boto3.client): Boto3 Transfer Family client

    Returns:
        list: A list of server IDs that were deleted

    Raises:
        ClientError: If there's an issue with the AWS API calls
    """
    logger.info("Starting cleanup of expired servers")
    servers = transfer.list_servers()
    current_time = datetime.utcnow()
    deleted_servers = []
    
    for server in servers['Servers']:
        server_id = server['ServerId']
        tags = transfer.list_tags_for_resource(Arn=server['Arn'])['Tags']
        expiration_time = next((tag['Value'] for tag in tags if tag['Key'] == 'ExpirationTime'), None)
        
        if expiration_time and datetime.fromisoformat(expiration_time) <= current_time:
            logger.info(f"Deleting expired server: {server_id}")
            transfer.delete_server(ServerId=server_id)
            deleted_servers.append(server_id)
    
    logger.info(f"Cleanup completed. Deleted servers: {deleted_servers}")
    return deleted_servers
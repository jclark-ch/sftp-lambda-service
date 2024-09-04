import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    """
    Retrieves a secret from AWS Secrets Manager.

    This function uses the AWS Secrets Manager service to securely retrieve
    sensitive information such as API keys, passwords, or other configuration
    data that shouldn't be hardcoded or stored in plain text.

    Args:
        secret_name (str): The name or ARN of the secret to retrieve

    Returns:
        str or bytes: The secret value. If the secret is stored as a string, 
        it returns a string. If it's stored as binary, it returns bytes.

    Raises:
        ClientError: If there's an issue retrieving the secret from AWS Secrets Manager.
        This could be due to permissions issues, network problems, or if the secret doesn't exist.

    Usage:
        try:
            db_password = get_secret("my-db-password")
            # Use db_password to connect to database
        except ClientError as e:
            # Handle error, e.g., log it or raise a custom exception
            logger.error(f"Couldn't retrieve secret: {e}")
    """
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            return get_secret_value_response['SecretBinary']
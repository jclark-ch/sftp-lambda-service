# SFTP Lambda Project

This project implements a serverless SFTP service using AWS Lambda, AWS Transfer Family, and S3. It allows for the creation of temporary SFTP servers with configurable lifetimes and automated cleanup.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Deployment](#deployment)
   - [CloudFormation](#cloudformation)
   - [Terraform](#terraform)
5. [Usage](#usage)
6. [Testing](#testing)
7. [Security Considerations](#security-considerations)
8. [Contributing](#contributing)

## Features

- Create temporary SFTP servers on-demand
- Configure server lifetime
- Automatic cleanup of expired servers
- IP-based access restrictions
- Secure storage of SFTP files in S3
- Supports both CloudFormation and Terraform for infrastructure deployment

## Prerequisites

- AWS Account
- AWS CLI configured with appropriate permissions
- Python 3.8 or higher
- Pip (Python package manager)
- Terraform (for Terraform deployment option)

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/sftp-lambda-project.git
   cd sftp-lambda-project
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure AWS credentials:
   ```
   aws configure
   ```

## Deployment

### CloudFormation

1. Update the `infrastructure/cloudformation/template.yaml` file with your specific configurations.

2. Run the deployment script:
   ```
   ./scripts/deploy_cloudformation.sh create
   ```

   To update an existing stack, use:
   ```
   ./scripts/deploy_cloudformation.sh update
   ```

### Terraform

1. Update the `infrastructure/terraform/*.tf` files with your specific configurations.

2. Run the Terraform deployment script:
   ```
   ./scripts/deploy_terraform.sh plan
   ```

   Review the plan, and if everything looks correct, apply the changes:
   ```
   ./scripts/deploy_terraform.sh apply
   ```

## Usage

After deployment, you can create a temporary SFTP server by invoking the Lambda function with the following JSON payload:

```json
{
  "customer_id": "example-customer",
  "ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
  "allowed_ips": ["203.0.113.0/24"],
  "lifetime_minutes": 60
}
```

The function will return the SFTP server details, including the hostname and username.

## Testing

To run the test suite:

```
./scripts/run_tests.sh all
```

This will run both unit and integration tests (if available) and generate a coverage report.

## Security Considerations

- All S3 buckets are encrypted and configured to block public access.
- Lambda functions use KMS for environment variable encryption.
- IP-based restrictions can be applied to SFTP users.
- Regular security audits should be performed.
- Keep all dependencies up to date.

Refer to `security_checklist.md` for a comprehensive security checklist.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

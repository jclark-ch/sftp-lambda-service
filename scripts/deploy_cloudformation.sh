#!/bin/bash
set -e

# Configuration
STACK_NAME="sftp-lambda-stack"
TEMPLATE_FILE="infrastructure/cloudformation/template.yaml"
S3_BUCKET="your-deployment-bucket"
AWS_REGION="us-west-2"  # Change this to your preferred region

# Function to display script usage
usage() {
    echo "Usage: $0 [create|update]"
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    usage
fi

# Validate the argument
case "$1" in
    create|update) ACTION=$1 ;;
    *) usage ;;
esac

echo "Packaging Lambda functions..."
# Package the main Lambda function
pip install -r requirements.txt -t src/package
cp src/lambda_function.py src/package/
cd src/package
zip -r ../../lambda-function.zip .
cd ../..

# Package the cleanup Lambda function
cp src/cleanup_function.py src/package/
cd src/package
zip -r ../../cleanup-function.zip .
cd ../..

# Clean up the package directory
rm -rf src/package

echo "Uploading Lambda packages to S3..."
aws s3 cp lambda-function.zip s3://$S3_BUCKET/lambda-function.zip
aws s3 cp cleanup-function.zip s3://$S3_BUCKET/cleanup-function.zip

echo "Deploying CloudFormation stack..."
if [ "$ACTION" == "create" ]; then
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --capabilities CAPABILITY_IAM \
        --parameters ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET \
        --region $AWS_REGION
    
    echo "Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $AWS_REGION
else
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --capabilities CAPABILITY_IAM \
        --parameters ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET \
        --region $AWS_REGION
    
    echo "Waiting for stack update to complete..."
    aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $AWS_REGION
fi

echo "Deployment completed successfully!"
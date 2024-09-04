#!/bin/bash
set -e

# Configuration
TERRAFORM_DIR="infrastructure/terraform"
AWS_REGION="us-west-2"  # Change this to your preferred region

# Function to display script usage
usage() {
    echo "Usage: $0 [plan|apply]"
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    usage
fi

# Validate the argument
case "$1" in
    plan|apply) ACTION=$1 ;;
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

echo "Moving Lambda packages to Terraform directory..."
mv lambda-function.zip $TERRAFORM_DIR/
mv cleanup-function.zip $TERRAFORM_DIR/

echo "Changing to Terraform directory..."
cd $TERRAFORM_DIR

echo "Initializing Terraform..."
terraform init

if [ "$ACTION" == "plan" ]; then
    echo "Creating Terraform plan..."
    terraform plan -var="aws_region=$AWS_REGION" -out=tfplan
    echo "Terraform plan created. Review the plan above."
else
    echo "Applying Terraform changes..."
    terraform apply -var="aws_region=$AWS_REGION" -auto-approve
    echo "Terraform changes applied successfully!"
fi

cd ../..
echo "Deployment process completed!"
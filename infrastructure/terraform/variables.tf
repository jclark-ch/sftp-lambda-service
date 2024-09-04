variable "aws_region" {
  description = "The AWS region to deploy to"
  default     = "us-west-2"
}

variable "env" {
  description = "Environment (dev, staging, prod)"
  default     = "dev"
}

variable "vpc_id" {
  description = "VPC ID for Lambda function"
}

variable "subnet_ids" {
  description = "Subnet IDs for Lambda function"
  type        = list(string)
}
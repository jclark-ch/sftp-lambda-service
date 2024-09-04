provider "aws" {
  region = var.aws_region
}

resource "aws_lambda_function" "sftp_lambda" {
  filename      = "lambda-function.zip"
  function_name = "sftp-lambda-function"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.lambda_handler"
  
  source_code_hash = filebase64sha256("lambda-function.zip")

  runtime = "python3.8"

  environment {
    variables = {
      ENV = var.env
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.lambda_sg.id]
  }

  kms_key_arn = aws_kms_key.sftp_lambda_key.arn
}

resource "aws_lambda_function" "sftp_cleanup_lambda" {
  filename      = "cleanup-function.zip"
  function_name = "sftp-cleanup-function"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.lambda_handler"
  
  source_code_hash = filebase64sha256("cleanup-function.zip")

  runtime = "python3.8"
}

resource "aws_cloudwatch_event_rule" "every_five_minutes" {
  name                = "every-five-minutes"
  description         = "Fires every five minutes"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "cleanup_every_five_minutes" {
  rule      = aws_cloudwatch_event_rule.every_five_minutes.name
  target_id = "sftp_cleanup_lambda"
  arn       = aws_lambda_function.sftp_cleanup_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_cleanup_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sftp_cleanup_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_five_minutes.arn
}

resource "aws_iam_role" "lambda_exec" {
  name = "sftp_lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_exec_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_exec.name
}

resource "aws_iam_role_policy" "sftp_s3_access" {
  name = "sftp_s3_access"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "transfer:*",
          "s3:*"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_security_group" "lambda_sg" {
  name        = "sftp-lambda-sg"
  description = "Security group for SFTP Lambda function"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_kms_key" "sftp_lambda_key" {
  description             = "KMS key for SFTP Lambda encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_alias" "sftp_lambda_key_alias" {
  name          = "alias/sftp-lambda-key"
  target_key_id = aws_kms_key.sftp_lambda_key.key_id
}
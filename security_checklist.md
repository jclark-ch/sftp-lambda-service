# Simplified Security Checklist for SFTP Lambda Project

## AWS Configuration
- [ ] IAM roles use least privilege principle
- [ ] S3 bucket has server-side encryption enabled
- [ ] S3 bucket blocks public access
- [ ] Lambda functions use environment variables for sensitive data
- [ ] KMS is used to encrypt Lambda environment variables

## SFTP Server Security
- [ ] SFTP servers use the latest security policy
- [ ] IP-based restrictions are implemented for SFTP users
- [ ] SSH keys are used for authentication (not passwords)

## Code Security
- [ ] Input data is validated and sanitized
- [ ] Dependencies are regularly updated
- [ ] Secrets are not hardcoded in the source code

## Operational Security
- [ ] CloudWatch logs are enabled for Lambda functions
- [ ] CloudTrail is enabled for API call logging
- [ ] Automated cleanup of expired SFTP servers is implemented

## Testing
- [ ] Unit tests cover critical functions
- [ ] Integration tests verify end-to-end functionality
- [ ] Manual security review is performed before major releases

## Compliance
- [ ] Data retention policies are defined and implemented
- [ ] User data is handled in compliance with relevant regulations
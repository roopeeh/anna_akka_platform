"""
IAM Infrastructure Module
Handles IAM roles, policies, and permissions for Lambda and Cognito
"""

import pulumi
import pulumi_aws as aws
import json

def create_iam_infrastructure(project_name: str, environment: str, tables):
    """Create IAM roles and policies"""
    
    # IAM Role for Lambda
    lambda_role = aws.iam.Role(f"{project_name}-lambda-role",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com",
                },
            }],
        }),
        tags={
            "Name": f"{project_name}-lambda-role",
            "Environment": environment,
        }
    )

    # Attach policies to Lambda role
    lambda_basic_policy = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-basic",
        role=lambda_role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    )
    
    lambda_vpc_policy = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-vpc",
        role=lambda_role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
    )

    # DynamoDB policy
    dynamodb_policy = aws.iam.Policy(f"{project_name}-dynamodb-policy",
        policy=pulumi.Output.all(*[table.arn for table in tables.values()]).apply(lambda arns: json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:BatchWriteItem",
                    ],
                    "Resource": arns + [f"{arn}/index/*" for arn in arns],
                },
            ],
        })),
        tags={
            "Name": f"{project_name}-dynamodb-policy",
            "Environment": environment,
        }
    )
    
    lambda_dynamodb_policy_attachment = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-dynamodb",
        role=lambda_role.name,
        policy_arn=dynamodb_policy.arn
    )

    # SNS policy for SMS functionality
    sns_policy = aws.iam.Policy(f"{project_name}-sns-policy",
        policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sns:Publish"
                    ],
                    "Resource": "*"
                }
            ],
        }),
        tags={
            "Name": f"{project_name}-sns-policy",
            "Environment": environment,
        }
    )

    lambda_sns_policy_attachment = aws.iam.RolePolicyAttachment(f"{project_name}-lambda-sns",
        role=lambda_role.name,
        policy_arn=sns_policy.arn
    )

    # IAM Role for Cognito SMS
    cognito_sms_role = aws.iam.Role(f"{project_name}-cognito-sms-role",
        name=f"{project_name}-{environment}-cognito-sms-role",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {
                    "Service": "cognito-idp.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }]
        }),
        tags={
            "Name": f"{project_name}-cognito-sms-role",
            "Environment": environment,
        }
    )

    # Create custom SMS policy for Cognito
    cognito_sms_policy = aws.iam.Policy(f"{project_name}-cognito-sms-policy",
        name=f"{project_name}-{environment}-cognito-sms-policy",
        description="Policy for Cognito SMS functionality",
        policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sns:Publish"
                    ],
                    "Resource": "*"
                }
            ]
        }),
        tags={
            "Name": f"{project_name}-cognito-sms-policy",
            "Environment": environment,
        }
    )

    # Attach the custom SMS policy
    cognito_sms_policy_attachment = aws.iam.RolePolicyAttachment(f"{project_name}-cognito-sms-policy-attachment",
        role=cognito_sms_role.name,
        policy_arn=cognito_sms_policy.arn
    )

    return {
        "lambda_role": lambda_role,
        "cognito_sms_role": cognito_sms_role,
        "cognito_sms_policy": cognito_sms_policy
    } 
"""
Cognito Infrastructure Module
Handles Cognito User Pool and authentication resources
"""

import pulumi
import pulumi_aws as aws
import pulumi_random as random

def create_cognito_infrastructure(project_name: str, environment: str, cognito_sms_role):
    """Create Cognito User Pool and related resources"""
    
    # Cognito User Pool
    cognito_user_pool = aws.cognito.UserPool(f"{project_name}-user-pool",
        name=f"{project_name}-user-pool",
        username_attributes=["phone_number"],
        auto_verified_attributes=["phone_number"],
        password_policy={
            "minimum_length": 8,
            "require_lowercase": True,
            "require_numbers": True,
            "require_symbols": False,
            "require_uppercase": True,
        },
        account_recovery_setting={
            "recovery_mechanisms": [{
                "name": "verified_phone_number",
                "priority": 1,
            }],
        },
        verification_message_template={
            "default_email_option": "CONFIRM_WITH_CODE",
        },
        mfa_configuration="OPTIONAL",
        software_token_mfa_configuration={
            "enabled": True,
        },
        sms_configuration=aws.cognito.UserPoolSmsConfigurationArgs(
            external_id=f"{project_name}-sms-config",
            sns_caller_arn=cognito_sms_role.arn,
            sns_region=pulumi.Config().get("aws:region") or "ap-south-1",
        ),
        tags={
            "Name": f"{project_name}-user-pool",
            "Environment": environment,
        }
    )

    # Cognito User Pool Client
    cognito_user_pool_client = aws.cognito.UserPoolClient(f"{project_name}-user-pool-client",
        name=f"{project_name}-user-pool-client",
        user_pool_id=cognito_user_pool.id,
        generate_secret=False,
        explicit_auth_flows=[
            "ALLOW_USER_PASSWORD_AUTH",
            "ALLOW_REFRESH_TOKEN_AUTH",
            "ALLOW_USER_SRP_AUTH",
        ],
        read_attributes=["phone_number", "email", "name"],
        write_attributes=["phone_number", "email", "name"],
        supported_identity_providers=["COGNITO"],
    )

    return {
        "cognito_user_pool": cognito_user_pool,
        "cognito_user_pool_client": cognito_user_pool_client
    } 
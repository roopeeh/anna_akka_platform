"""
VPC and Networking Infrastructure Module
Handles VPC, subnets, security groups, and networking components
"""

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx

def create_vpc_infrastructure(project_name: str, environment: str):
    """Create VPC and networking infrastructure"""
    
    # VPC and Networking - Optimized for faster deployment
    vpc = awsx.ec2.Vpc(f"{project_name}-vpc",
        cidr_block="10.0.0.0/16",
        number_of_availability_zones=2,
        subnet_specs=[
            awsx.ec2.SubnetSpecArgs(
                type=awsx.ec2.SubnetType.PRIVATE,
                cidr_mask=24,
            ),
            awsx.ec2.SubnetSpecArgs(
                type=awsx.ec2.SubnetType.PUBLIC,
                cidr_mask=24,
            ),
        ],
        subnet_strategy=awsx.ec2.SubnetAllocationStrategy.AUTO,
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags={
            "Name": f"{project_name}-vpc",
            "Environment": environment,
        }
    )

    # Security Group for Lambda
    lambda_sg = aws.ec2.SecurityGroup(f"{project_name}-lambda-sg",
        vpc_id=vpc.vpc_id,
        description="Security group for Lambda functions",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["0.0.0.0/0"],
                description="HTTPS outbound"
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
        tags={
            "Name": f"{project_name}-lambda-sg",
            "Environment": environment,
        }
    )

    return {
        "vpc": vpc,
        "lambda_sg": lambda_sg,
        "private_subnet_ids": vpc.private_subnet_ids,
        "public_subnet_ids": vpc.public_subnet_ids,
        "vpc_id": vpc.vpc_id
    } 
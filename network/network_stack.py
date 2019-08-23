"""
Defines a NetworkStack
"""

from aws_cdk import (
    aws_ec2 as ec2,
    core
)

class NetworkStack(core.Stack):
    """
    VPC and supporting resources
    """

    def __init__(self, scope=None, name=None, *, env=None, stack_name=None, tags=None):
        """
        Construct resources
        """
        super().__init__(scope=scope, name=name, env=env, stack_name=stack_name, tags=tags)

        # Create the VPC
        vpc = ec2.Vpc(
            self,
            f"{name}-vpc",
            cidr=ec2.Vpc.DEFAULT_CIDR_RANGE,
            enable_dns_support=True,
            enable_dns_hostnames=True,
            max_azs=1,
            nat_gateways=0,
            subnet_configuration=[ec2.SubnetConfiguration(
                name=f"{name}-subnet",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=28
            )]
        )

        # Find the default Security Group and add a rule to it
        ec2.SecurityGroup.from_security_group_id(
            self,
            f"{name}-sg",
            security_group_id=vpc.vpc_default_security_group
        ).add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(25565),
            description="Port that the Minecraft server communicates on"
        )

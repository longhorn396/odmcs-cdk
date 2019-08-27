"""
Defines a InstanceStack
"""

from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    core
)

class InstanceStack(core.Stack):
    """
    EC2 instance with Minecraft server installed
    """

    def __init__(self, scope=None, name=None, ami=None, subnet=None, *, env=None, stack_name=None, tags=None):
        """
        Construct resources
        """
        super().__init__(scope=scope, name=name, env=env, stack_name=stack_name, tags=tags)

        # Role for SSM to manage the instance
        role = iam.Role(
            self,
            f"{name}-role",
            assumed_by=iam.ServicePrincipal("ec2"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess")
            ],
            role_name=f"{name}-role"
        )

        # Attach role to instance profile
        profile = iam.CfnInstanceProfile(
            self,
            f"{name}-profile",
            roles=[role.role_name],
            instance_profile_name=f"{name}-profile"
        )

        # Read user data from a script in this directory
        user_data = ec2.UserData.for_linux()
        with open("instance/userdata.sh") as sh:
            user_data.add_commands(*sh.read().splitlines())

        # Create the instance
        ec2.CfnInstance(
            self,
            f"{name}-server",
            iam_instance_profile=profile.instance_profile_name,
            image_id=ami,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL).to_string(),
            subnet_id=subnet,
            user_data=user_data.render(),
            tags=[{"key": "Name", "value": f"{name}-server"}]
        )
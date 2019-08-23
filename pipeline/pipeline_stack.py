"""
Defines a PipelineStack
"""

from aws_cdk import (
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
    aws_iam as iam,
    aws_s3 as s3,
    core
)

class PipelineStack(core.Stack):
    """
    AWS CodePipeline and supporting resources
    """

    def __init__(self, scope=None, name=None, *, env=None, stack_name=None, tags=None):
        """
        Construct resources
        """
        super().__init__(scope=scope, name=name, env=env, stack_name=stack_name, tags=tags)

        # Artifact passed from one stage to the next
        source_output = codepipeline.Artifact("SourceOutput")

        # GitHub repository this code is hosted in
        github_repo = actions.GitHubSourceAction(
            action_name="SourceAction",
            oauth_token=core.SecretValue.secrets_manager("GitHub_to_CodePipeline_OAUTH",
                                                         json_field="GitHubPersonalAccessToken"),
            output=source_output,
            owner="longhorn396",
            repo="odmcs-cdk",
            branch="master",
            trigger=actions.GitHubTrigger.WEBHOOK
        )

        # CodeBuild Project to go into the pipeline
        pipeline_project = codebuild.PipelineProject(
            self,
            f"{name}-build",
            badge=False,
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "nodejs": 10,
                            "python": 3.7
                        },
                        "commands": [
                            "apt-get update -y",
                            "npm install -g aws-cdk",
                            "pip install --upgrade pip",
                            "pip install -r requirements.txt",
                            "cdk bootstrap"
                        ]
                    },
                    "pre_build": {
                        "commands": [
                            "cdk ls",
                            "cdk synth"
                        ]
                    },
                    "build": {
                        "commands": [
                            "cdk diff || (cdk deploy '*')"
                        ]
                    },
                    "post_build": {
                        "commands": [
                            "cdk diff"
                        ]
                    }
                }
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_2_0
            ),
            project_name=f"{name}-build"
        )

        # Grant CloudFormation permissions to the project
        pipeline_project.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudformation:*"],
            effect=iam.Effect.ALLOW,
            resources=["*"]
        ))

        # Wrap the project in an action
        build_action = actions.CodeBuildAction(
            action_name="BuildAction",
            input=source_output,
            project=pipeline_project
        )

        # Set up the CodePipeline
        pipeline = codepipeline.Pipeline(
            self,
            f"{name}-pipeline",
            artifact_bucket=s3.Bucket.from_bucket_name(
                self,
                "artifact-bucket",
                "ddrawhorn-artifacts"
            ),
            pipeline_name=f"{name}-pipeline",
            restart_execution_on_update=True
        )

        # Add stages to the pipeline
        pipeline.add_stage(stage_name="Source", actions=[github_repo])
        pipeline.add_stage(stage_name="Build", actions=[build_action])

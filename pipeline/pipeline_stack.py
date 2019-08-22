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
    pass
    """

    def __init__(self, scope, unique_id, **kwargs):
        """
        pass
        """
        super().__init__(scope, unique_id, **kwargs)

        source_output = codepipeline.Artifact("SourceOutput")
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
        pipeline_project = codebuild.PipelineProject(
            self,
            "project",
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
                            "pip install -r requirements.txt",
                            "cdk bootstrap"
                        ]
                    },
                    "pre_build": {
                        "commands": [
                            "cdk ls",
                            "cdk synth",
                            "cdk diff"
                        ]
                    }
                }
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_2_0
            ),
            project_name="odmcs-build"
        )
        pipeline_project.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudformation:*"],
            effect=iam.Effect.ALLOW,
            resources=["*"]
        ))
        build_action = actions.CodeBuildAction(
            action_name="BuildAction",
            input=source_output,
            project=pipeline_project
        )
        pipeline = codepipeline.Pipeline(
            self,
            "pipeline",
            artifact_bucket=s3.Bucket.from_bucket_name(
                self,
                "artifact-bucket",
                "ddrawhorn-artifacts"
            ),
            pipeline_name="odmcs-pipeline",
            restart_execution_on_update=True
        )
        pipeline.add_stage(stage_name="Source", actions=[github_repo])
        pipeline.add_stage(stage_name="Build", actions=[build_action])

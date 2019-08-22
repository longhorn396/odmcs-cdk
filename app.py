#!/usr/bin/env python3

from aws_cdk import core

from pipeline.pipeline_stack import PipelineStack


app = core.App()
PipelineStack(app, "odmcs-pipeline")
app.synth()

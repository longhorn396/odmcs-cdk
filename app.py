#!/usr/bin/env python3

from aws_cdk import core

from pipeline.pipeline_stack import PipelineStack
from network.network_stack import NetworkStack

app = core.App()
PipelineStack(app, "odmcs-cicd")
NetworkStack(app, "odmcs-network")
app.synth()

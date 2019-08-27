#!/usr/bin/env python3

from aws_cdk import core

from pipeline.pipeline_stack import PipelineStack
from network.network_stack import NetworkStack
from instance.instance_stack import InstanceStack

app = core.App()
PipelineStack(app, "odmcs-cicd")
network = NetworkStack(app, "odmcs-network")
InstanceStack(app, "odmcs-instance", "ami-05c1fa8df71875112", network.subnet)
app.synth()

#!/usr/bin/env python3

from aws_cdk import core

from odmcs_cdk.odmcs_cdk_stack import OdmcsCdkStack


app = core.App()
OdmcsCdkStack(app, "odmcs-cdk")

app.synth()

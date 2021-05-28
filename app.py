#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from sam_pipeline_module.sam_pipeline_module import SamPipelineModule


app = cdk.App()
SamPipelineModule(app, "SamPipelineModule")

app.synth()

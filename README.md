# SAM Pipeline Cloudformation Module

A personal example of using AWS cdk to generate a cloudformation template to be used as a cloudformation module. 

## Pre-reqs
- AWS cdk
- CloudFormation cli
  
## Use

To generate the template

`cdk synth -j > fragments/synth.json`

To deploy the Cloudformation Module

`cfn submit --region *region-identifier*`
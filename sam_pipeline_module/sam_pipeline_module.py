from aws_cdk import (core as cdk, 
                    aws_codepipeline as codepipeline,
                    aws_codepipeline_actions as codepipeline_actions,
                    aws_codebuild as codebuild, 
                    aws_codecommit as codecommit)


class SamPipelineModule(cdk.Stack):
    
    def addDeployStage(bucketName, app):
        # deployAction = codepipeline_actions
        pass

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        app = cdk.CfnParameter(self, "app", type="String").value_as_string

        repo = codecommit.Repository(self, id="cc", repository_name=app)

        sourceOutput = codepipeline.Artifact()
        pipeline = codepipeline.Pipeline(self, id="p", pipeline_name="{}-pipeline".format(app))
        sourceAction = codepipeline_actions.CodeCommitSourceAction(
            action_name='CodeCommit',
            repository=repo,
            output=sourceOutput
        )
        pipeline.add_stage(stage_name="Source", actions=[sourceAction])

        pipeline.artifact_bucket.s3_url_for_object()

        buildOutput = codepipeline.Artifact()

        ## Create the CodeBuild Porject
        buildSpec = codebuild.BuildSpec.from_object({
            "version": "0.2",
            "phases": {
                "install": {
                    "runtime-versions": {
                        "python": 3.8
                    }
                },
                "build": {
                    "commands": ["sam build"]
                    
                },
                "post_build": {  
                    "commands": ["sam package --s3-bucket {} --output-template-file packaged.yaml".format(pipeline.artifact_bucket.bucket_name)]
                }
            },
            "artifacts": {
                "discard-paths": "yes",
                "files": ["packaged.yaml"]
            }
        })
        project = codebuild.PipelineProject(self, id="bp", build_spec=buildSpec)

        ## Add CodeBuild Project as a Pipeline Stage
        buildAction = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project,
            input=sourceOutput,
            outputs=[buildOutput]
        )
        pipeline.add_stage(stage_name="Build", actions=[buildAction])
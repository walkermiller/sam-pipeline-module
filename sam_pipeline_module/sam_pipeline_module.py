from aws_cdk import (core as cdk, 
                    aws_codepipeline as codepipeline,
                    aws_codepipeline_actions as codepipeline_actions,
                    aws_codebuild as codebuild, 
                    aws_codecommit as codecommit)

def createDeployStage(buildArtifact: codepipeline.Artifact, app, deployStage):
    create_changeSet = codepipeline_actions.CloudFormationCreateReplaceChangeSetAction(
        action_name="{}-Create-Change".format(deployStage),
        stack_name="{}-{}".format(app, deployStage),
        template_path=buildArtifact.at_path("packaged.yaml"),
        change_set_name="triggered change",
        admin_permissions=True,
        run_order=1)

    execute_changeSet = codepipeline_actions.CloudFormationExecuteChangeSetAction(
        action_name="{}-Execute-Change".format(deployStage),
        change_set_name="triggered change",
        stack_name="{}-{}".format(app, deployStage),
        run_order=2)

    return [create_changeSet, execute_changeSet]

class SamPipelineModule(cdk.Stack):
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
                    "commands": ["sam package --s3-bucket s3://{} --output-template-file packaged.yaml".format(pipeline.artifact_bucket.bucket_name)]
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

        ## Add Deploy Stage
        pipeline.add_stage(stage_name="dev-Deploy", actions=createDeployStage(buildOutput, app, "dev"))
        pipeline.add_stage(stage_name="qa-Deploy", actions=createDeployStage(buildOutput, app, "qa"))
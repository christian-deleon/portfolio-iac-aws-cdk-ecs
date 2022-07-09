import typing

from aws_cdk import (
    Stack, 
    Duration, 
    PhysicalName,
    aws_iam as iam, 
    aws_ecr as ecr, 
    aws_events as events, 
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_events_targets as events_targets, 
    aws_codepipeline_actions as codepipeline_actions,
)
from constructs import Construct

from portfolio.region_stack.region_persistent_stack import RegionPersistentStack
from portfolio.utils import construct_name

from config import config


class BuildPipelineStack(Stack):
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        connection_arn: str, 
        region_persistent_stacks: typing.Mapping[str, RegionPersistentStack], 
        **kwargs
        ) -> None:
        
        super().__init__(scope, construct_id, **kwargs)

        self.repository = ecr.Repository(self, "PortfolioRepository", 
            repository_name=PhysicalName.GENERATE_IF_NEEDED
        )

        destinations = []
        for region, persistent_stack in region_persistent_stacks.items():
            if region == config['account.main_region']:
                continue

            destinations.append(ecr.CfnReplicationConfiguration.ReplicationDestinationProperty(
                region=region,
                registry_id=config['account.id']
            ))

            rule = events.Rule(self, 
                construct_name('main-region-ecr-routing', region), 
                event_pattern=events.EventPattern(
                    source=["aws.ecr"], 
                    detail={
                        "action-type": ["PUSH"],
                        "result": ["SUCCESS"],
                        "repository-name": [self.repository.repository_name], 
                        "image-tag": ["latest"]
                    }
                )
            )

            rule.add_target(events_targets.EventBus(persistent_stack.ecr_event_bus))

        if destinations:
            ecr.CfnReplicationConfiguration(self, "ReplicationConfiguration",
                replication_configuration=ecr.CfnReplicationConfiguration.ReplicationConfigurationProperty(
                    rules=[
                        ecr.CfnReplicationConfiguration.ReplicationRuleProperty(
                            destinations=destinations
                        )
                    ]
                )
            )

        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            connection_arn=connection_arn, 
            owner=config['github.owner'],
            repo=config['github.repo'],
            output=source_output,
        )

        role = iam.Role(self, "Role",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:*",
                ],
                resources=["*"]
            )
        )

        main_region = config['account.main_region']
        aws_uri = f"{config['account.id']}.dkr.ecr.{main_region}.amazonaws.com"
        image_uri = f"{self.repository.repository_uri}:latest"

        project = codebuild.PipelineProject(self, "Project",
            role=role, 
            timeout=Duration.minutes(10), 
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER), 
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_4_0, 
                privileged=True, 
            ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "pre_build": {
                        "commands": [
                            "echo logging into Amazon ECR...",
                            f"aws ecr get-login-password --region {main_region} | docker login --username AWS --password-stdin {aws_uri}",
                            f"docker pull {image_uri} || true"
                        ]
                    },
                    "build": {
                        "commands": [
                            "echo building docker image...",
                            f"docker build --cache-from {image_uri} -t {image_uri} . || docker build -t {image_uri} ."
                        ]
                    },
                    "post_build": {
                        "commands": [
                            "echo pushing docker image...",
                            f"docker push {image_uri}"
                        ]
                    }
                },
            }),
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project,
            input=source_output,
        )

        codepipeline.Pipeline(self, "Pipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        source_action
                    ]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        build_action
                    ]
                )
            ]
        )

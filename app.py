#!/usr/bin/env python3
import aws_cdk as cdk

from portfolio.route53_stack import Route53Stack
from portfolio.build_pipeline_stack import BuildPipelineStack
from portfolio.github_connection_stack import GitHubConnectionStack

from portfolio.region_stack.region_parent_stack import RegionParentStack
from portfolio.region_stack.persistent_parent_stack import PersistentParentStack

from portfolio.utils import construct_name

from config import config


app = cdk.App()

main_env = cdk.Environment(
    account=config['account.id'], 
    region=config['account.main_region']
)

github_connection_stack = GitHubConnectionStack(
    app, 
    "GitHubConnection", 
    env=main_env
)

persistent_parent_stack = PersistentParentStack(
    app, 
    "PersistentParentStack", 
    env=main_env
)

pipeline = BuildPipelineStack(
    app, 
    "PipelineStack", 
    connection_arn=github_connection_stack.connection_arn, 
    region_persistent_stacks=persistent_parent_stack.region_persistent_stacks, 
    env=main_env
)

if config['route53.zone_name'] in ['None', None]:
    hosted_zone_id = None

else:
    route53_stack = Route53Stack(
        app, 
        "Route53Stack", 
        env=main_env,
    )
    hosted_zone_id = route53_stack.hosted_zone.hosted_zone_id

for region, persistent_stack in persistent_parent_stack.region_persistent_stacks.items():
    RegionParentStack(
        app, 
        construct_name("ParentStack", region), 
        persistent_stack=persistent_stack, 
        ecr_repository=pipeline.repository, 
        hosted_zone_id=hosted_zone_id, 
        region=region
    )

app.synth()

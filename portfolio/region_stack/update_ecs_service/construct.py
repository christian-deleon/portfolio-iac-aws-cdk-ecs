from pathlib import Path

from aws_cdk import (
    Duration, 
    aws_events as events, 
    aws_events_targets as targets, 
    aws_iam as iam,
    aws_lambda as lambda_,
)
from constructs import Construct

from portfolio.region_stack.region_persistent_stack import RegionPersistentStack


class UpdateECSService(Construct):

    def __init__(
        self, 
        scope: "Construct", 
        id: str, 
        cluster_arn: str, 
        service_arn: str, 
        persistent_stack: RegionPersistentStack
        ) -> None:

        super().__init__(scope, id)

        lambda_role = iam.Role(self, "Role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess"))

        lambda_path = str(Path(Path(__file__).parent.resolve(), "lambda"))

        function = lambda_.Function(self, "Function",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='handler.handler',
            code=lambda_.Code.from_asset(lambda_path),
            timeout=Duration.seconds(5),
            memory_size=256,
            role=lambda_role,
            environment={
                "ECS_CLUSTER_ARN": cluster_arn,
                "ECS_SERVICE_ARN": service_arn,
            },
        )

        rule = events.Rule(self, "Rule",
            event_bus=persistent_stack.ecr_event_bus, 
            event_pattern=events.EventPattern(
                source=["aws.ecr"], 
                detail={
                    "action-type": ["PUSH"],
                    "result": ["SUCCESS"],
                    "repository-name": ["portfolio"], 
                    "image-tag": ["latest"]
                }
            )
        )

        rule.add_target(targets.LambdaFunction(function))

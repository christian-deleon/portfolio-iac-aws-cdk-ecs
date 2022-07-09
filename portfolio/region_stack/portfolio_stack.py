from typing import Optional

from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ecr as ecr, 
    aws_route53 as route53, 
    aws_route53_targets as route53_targets,
    aws_ecs_patterns as ecs_patterns,
    aws_certificatemanager as certificatemanager,
)
from constructs import Construct

from portfolio.region_stack.region_persistent_stack import RegionPersistentStack
from portfolio.region_stack.update_ecs_service.construct import UpdateECSService

from config import config


class PortfolioStack(Stack):

    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        persistent_stack: RegionPersistentStack, 
        ecr_repository: ecr.Repository, 
        region: str, 
        hosted_zone_id: Optional[str] = None, 
        **kwargs
        ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        cluster = ecs.Cluster(self, "Cluster",
            vpc=persistent_stack.vpc,
            enable_fargate_capacity_providers=True,
        )

        execution_role = iam.Role(self, "ExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )
        execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )

        if hosted_zone_id:
            hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, "HostedZone",
                hosted_zone_id=hosted_zone_id,
                zone_name=config['route53.zone_name']
            )

            certificate = certificatemanager.Certificate(self, "Certificate",
                domain_name=config['route53.domain_name'],
                validation=certificatemanager.CertificateValidation.from_dns(hosted_zone=hosted_zone)
            )
            redirect_http = True

        else:
            certificate = None
            redirect_http = None

        image = ecs.ContainerImage.from_ecr_repository(
            repository=ecr_repository,
            tag="latest"
        )

        pattern = ecs_patterns.ApplicationLoadBalancedFargateService(self, "Service",
            cluster=cluster,
            memory_limit_mib=config['ecs.memory_limit_mib'],
            cpu=config['ecs.cpu'],
            desired_count=config['ecs.desired_count'],
            assign_public_ip=True,
            redirect_http=redirect_http,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            certificate=certificate,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=3000,
                execution_role=execution_role,
            ), 
            deployment_controller=ecs.DeploymentController(
                type=ecs.DeploymentControllerType.CODE_DEPLOY
            )
        )

        if hosted_zone_id:
            record = route53.ARecord(self, "AliasRecord",
                zone=hosted_zone, 
                record_name=config['route53.domain_name'], 
                target=route53.RecordTarget.from_alias(route53_targets.LoadBalancerTarget(pattern.load_balancer)),
            )

            recordSet: route53.CfnRecordSet = record.node.default_child
            recordSet.region = region
            recordSet.set_identifier = region

        UpdateECSService(self, "UpdateECSService", 
            cluster_arn=cluster.cluster_arn, 
            service_arn=pattern.service.service_arn, 
            persistent_stack=persistent_stack
        )

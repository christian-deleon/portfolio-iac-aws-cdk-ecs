import os

from boto3 import client


ecs = client("ecs")


def handler(event, context):
    ecs.update_service(
        cluster=os.environ['ECS_CLUSTER_ARN'], 
        service=os.environ['ECS_SERVICE_ARN'],
        forceNewDeployment=True
    )

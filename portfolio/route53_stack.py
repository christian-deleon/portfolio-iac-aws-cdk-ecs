from aws_cdk import (
    aws_route53 as route53, 
    Stack, 
)
from constructs import Construct

from config import config


class Route53Stack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, env, **kwargs) -> None:
        super().__init__(scope, construct_id, env=env, **kwargs)

        self.hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone",
            domain_name=config['route53.zone_name'],
        )

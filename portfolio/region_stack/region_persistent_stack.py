from aws_cdk import (
    Stack, 
    Environment, 
    aws_ec2 as ec2, 
    aws_events as events, 
)
from constructs import Construct

from portfolio.utils import construct_name

from config import config


class RegionPersistentStack(Stack):
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        region: str, 
        **kwargs
        ) -> None:

        self.env = Environment(
            account=config['account.id'], 
            region=region
        )

        super().__init__(scope, construct_id, env=self.env, **kwargs)
        
        self.vpc = ec2.Vpc(self, "VPC",
            subnet_configuration=[
                ec2.SubnetConfiguration(name="public", subnet_type=ec2.SubnetType.PUBLIC),
            ]
        )

        if region != config['account.main_region']:
            self.ecr_event_bus = events.EventBus(self, 
                construct_name('Bus', region), 
                event_bus_name='main-region-ecr-routing'
            )
        else:
            self.ecr_event_bus = events.EventBus.from_event_bus_name(self, 
                'EventBus', 
                event_bus_name='default'
            )

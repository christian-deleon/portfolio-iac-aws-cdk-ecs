from aws_cdk import (
    Stack, 
)
from constructs import Construct

from portfolio.region_stack.region_persistent_stack import RegionPersistentStack
from portfolio.utils import construct_name

from config import config


class PersistentParentStack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        if config['route53.zone_name'] in ['None', None]:
            regions = [config['account.main_region'], *config['account.other_regions']]
        else:
            regions = [config['account.main_region']]

        self.region_persistent_stacks = {}
        for region in regions:
            stack = RegionPersistentStack(
                self, 
                construct_name("PersistentStackECS", region), 
                region=region
            )
            self.region_persistent_stacks[region] = stack

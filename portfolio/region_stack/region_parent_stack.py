from typing import Optional

from aws_cdk import (
    Stack, 
    aws_ecr as ecr, 
)
from constructs import Construct

from portfolio.region_stack.portfolio_stack import PortfolioStack
from portfolio.region_stack.region_persistent_stack import RegionPersistentStack


class RegionParentStack(Stack):
    
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

        env = persistent_stack.env

        super().__init__(scope, construct_id, env=env, **kwargs)

        PortfolioStack(
            self, 
            "PortfolioStack", 
            persistent_stack=persistent_stack,
            ecr_repository=ecr_repository, 
            region=region,
            hosted_zone_id=hosted_zone_id,
            env=env
        )

        # Future Stacks Added here

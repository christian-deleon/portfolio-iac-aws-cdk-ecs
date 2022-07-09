from aws_cdk import (
    Stack, 
    aws_codestarconnections as codestarconnections, 
)
from constructs import Construct


class GitHubConnectionStack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        connection = codestarconnections.CfnConnection(self, "CfnConnection",
            connection_name='github-portfolio-connection-ecs',
            provider_type="GitHub",
        )
        self.connection_arn = connection.attr_connection_arn

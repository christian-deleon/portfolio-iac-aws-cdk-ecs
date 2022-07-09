
# My Personal Portfolio Infrastructure

## Deploying this infrastructure

1. Change directory to the architecture of your choice.

2. Configure your infrastructure with the `config.yaml` file.

   For the ECS CPU and Memory configuration
<div align="left">
  <img alt="Demo" src="./images/fargate_cpu_memory_chart.png" />
</div>

3. Synthesize the CloudFormation Templates:
    ```bash
    cdk synth
    ```

4. Deploy the GitHubConnection stack to connect your account to Github:
   ```bash
   cdk deploy GitHubConnection
   ```

5. Wait the stack to finish before continuing.

6. Accepting the GitHub connection 
   
   1. Go to [AWS CodeStar Connections](https://us-east-1.console.aws.amazon.com/codesuite/settings/connections).
   2. Choose the `github-portfolio-connection-ecs` connection.
   3. Click `Update pending connection`.

7. Deploy the PersistentParentStack and PipelineStackECS stacks:
   ```bash
   cdk deploy PersistentParentStack PipelineStack --require-approval="never"
   ```

8. Go to the [AWS CodePipeline Console](https://console.aws.amazon.com/codesuite/codepipeline/pipelines) and wait for the `PipelineStackECS` pipeline to finish.

9.  Deploy the remaining stacks:
   ```bash
   cdk deploy --all --require-approval="never"
   ``` 

## Updating ECS configuration

1. Update the `config.yaml` ecs values.

2. Re-deploy stacks:
   ```bash
   cdk deploy --all --require-approval="never"
   ``` 

## Destroying this infrastructure

If you want to destroy the stacks simply run:
   ```bash
   cdk destroy --all --force
   ```

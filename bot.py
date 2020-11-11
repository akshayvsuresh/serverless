from pprint import pprint
import boto3



client = boto3.resource('dynamodb')
table = client.Table('Serverless')
version = input("Enter the app version: ")
    
response = table.get_item(Key={'VersionID': version })
depId = response['Item']['DeploymentID']
eventId = response['Item']['ExecutionID']
print(depId)
print(eventId)


client = boto3.client('codedeploy')
response = client.put_lifecycle_event_hook_execution_status(
deploymentId=depId,
lifecycleEventHookExecutionId=eventId,
status="Failed")


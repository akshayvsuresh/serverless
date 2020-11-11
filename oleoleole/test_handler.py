import json
import os
import requests
import jsonpath
import boto3





def invoke_lambda(function_name):
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=function_name
    )
    
    return response


def code_deploy_event_status(depId, eventId, status):
    client = boto3.client('codedeploy')
    response = client.put_lifecycle_event_hook_execution_status(
        deploymentId=depId,
        lifecycleEventHookExecutionId=eventId,
        status=status
    )

    return response
    
    





def test_pre_traffic(event, context):
    
    client = boto3.resource('dynamodb')
    table = client.Table('Serverless')
    deployment_id = event['DeploymentId']
    versionid = os.getenv("APP_VERSION")
    life_cycle_event_hook_execution_id = event['LifecycleEventHookExecutionId']
    
    input = {'VersionID': versionid ,'DeploymentID': deployment_id ,'ExecutionID': life_cycle_event_hook_execution_id }
    response = table.put_item(Item=input)

    
    current_function_version = os.getenv("CurrentFunctionVersion")
    pre_test_rsp = invoke_lambda(current_function_version)
    deployment_id = event['DeploymentId']
    print(deployment_id)
    life_cycle_event_hook_execution_id = event['LifecycleEventHookExecutionId']
    print(life_cycle_event_hook_execution_id)

    ret = pre_test_rsp['Payload'].read()
    data = json.loads(ret)
    body = json.loads(data['body'])

    try:
        assert data['statusCode'] == 200
        assert body['version'] == os.getenv("APP_VERSION")
        code_deploy_event_status(deployment_id, life_cycle_event_hook_execution_id, 'Succeeded')
        print("Succeeded")
    except AssertionError:
        code_deploy_event_status(deployment_id, life_cycle_event_hook_execution_id, 'Failed')
        print("Failed")

def test_post_traffic(event, context):
    deployment_id = event['DeploymentId']
    life_cycle_event_hook_execution_id = event['LifecycleEventHookExecutionId']
    client1 = boto3.client('cloudformation')

    response = client1.describe_stacks(
    StackName='sam-python')
    

    response1 = response['Stacks']
    dicta = response1[0]
    url = dicta['Outputs'][0]['OutputValue']      
    response = requests.get(url)
    print(response)
    
    json_response = json.loads(response.text)
    print(json_response)
    pages = jsonpath.jsonpath(json_response,'message')
    pages1 = jsonpath.jsonpath(json_response,'version')
    #assert pages[0] == "Feelin' hot hotttt hot21!"
    #assert pages1[0] == "v2"
    
    
    try:
        assert pages[0] == "new code1"
        assert pages1[0] == "v7"
        code_deploy_event_status(deployment_id, life_cycle_event_hook_execution_id, 'Succeeded')
        print("Succeeded")
    except AssertionError:
        code_deploy_event_status(deployment_id, life_cycle_event_hook_execution_id, 'Failed')
        print("Failed")



    # code_deploy_event_status(deployment_id, life_cycle_event_hook_execution_id, 'Failed')
    #code_deploy_event_status(deployment_id, life_cycle_event_hook_execution_id, 'Succeeded')


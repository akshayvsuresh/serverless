from pprint import pprint
import boto3
import os 
version = input("Enter the version to deploy")
samdeploy="sam deploy --template-file ./packaged.yaml --stack-name sam-python --capabilities CAPABILITY_IAM --region us-east-1 --parameter-overrides AppVersion="+version
list = ['sam build','sam package --output-template-file packaged.yaml --s3-bucket akshayserverless',samdeploy]
for i in list:
    os.system(i)

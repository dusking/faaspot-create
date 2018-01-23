import boto3
import json
import uuid
import logging

from config import ACCOUNT_ID, ROLE_NAME
logger = logging.getLogger(__name__)


class AWS(object):
    def __init__(self):
        self.default_region = 'us-east-1'
        self.default_role = 'arn:aws:iam::{0}:role/service-role/{1}'.format(ACCOUNT_ID, ROLE_NAME)

    def create_function(self, function_name, repo_name, http_method, deploy_zip):
        aws_region = self.default_region
        role = self.default_role

        api_client = boto3.client('apigateway', region_name=aws_region)
        aws_lambda = boto3.client('lambda', region_name=aws_region)

        values = {
            'FunctionName': function_name,
            'Handler': 'handler.{0}'.format(function_name),
            'Code': {'ZipFile': open(deploy_zip, 'rb').read()},
            'Role': role,
            'Publish': True,
            'Runtime': 'python2.7',
            'Timeout': 30
        }
        response = aws_lambda.create_function(**values)
        logger.debug('Lambda created: {0}'.format(response))

        # Create a rest api
        rest_api = api_client.create_rest_api(
            name='AWS_Lambda'
        )
        aws_lambda_api_id = rest_api['id']

        # Get the rest api's root id
        root_id = api_client.get_resources(
            restApiId=rest_api['id']
        )['items'][0]['id']
        logger.debug('root_id: {0}'.format(root_id))

        # create resource
        resource_response = api_client.create_resource(
            restApiId=aws_lambda_api_id,
            parentId=root_id,  # resource id for the Base API path
            pathPart=function_name
        )
        logger.debug('Create rest resource: {0}'.format(resource_response))

        # create HTTP method
        put_method_resp = api_client.put_method(
            restApiId=aws_lambda_api_id,
            resourceId=resource_response['id'],
            httpMethod=http_method,
            authorizationType="NONE",
            apiKeyRequired=True
        )
        logger.debug('Created {0} method: {1}'.format(http_method, put_method_resp))

        lambda_version = aws_lambda.meta.service_model.api_version

        uri_data = {
            "aws-region": aws_region,
            "api-version": lambda_version,
            "aws-acct-id": "282231467242",
            "lambda-function-name": function_name,
            "httpMethod": http_method
        }

        uri = "arn:aws:apigateway:{aws-region}:lambda:path/{api-version}/functions/arn:aws:lambda:{aws-region}:{aws-acct-id}:function:{lambda-function-name}/invocations".format(
            **uri_data)

        # create integration
        integration_resp = api_client.put_integration(
            restApiId=aws_lambda_api_id,
            resourceId=resource_response['id'],
            httpMethod=http_method,
            type="AWS",
            integrationHttpMethod=http_method,
            uri=uri,
        )
        logger.debug('Created integration: {0}'.format(integration_resp))

        response = api_client.put_integration_response(
            restApiId=aws_lambda_api_id,
            resourceId=resource_response['id'],
            httpMethod=http_method,
            statusCode="200",
            selectionPattern=".*"
        )
        logger.debug('Put integration response: {0}'.format(response))

        # create method response
        response = api_client.put_method_response(
            restApiId=aws_lambda_api_id,
            resourceId=resource_response['id'],
            httpMethod=http_method,
            statusCode="200",
        )
        logger.debug('Put method response: {0}'.format(response))

        uri_data['aws-api-id'] = aws_lambda_api_id
        source_arn = "arn:aws:execute-api:{aws-region}:{aws-acct-id}:{aws-api-id}/*/{httpMethod}/{lambda-function-name}".format(
            **uri_data)

        aws_lambda.add_permission(
            FunctionName=function_name,
            StatementId=uuid.uuid4().hex,
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn
        )

        response = api_client.create_deployment(
            restApiId=aws_lambda_api_id,
            stageName=repo_name,
        )
        logger.debug('Created function with epi endpoint: {0}'.format(response))
        return "done"

    def update_function(self, function_name, deploy_zip):
        aws_lambda = boto3.client('lambda', region_name=self.default_region)
        response = aws_lambda.update_function_code(
            FunctionName=function_name,
            ZipFile=open(deploy_zip, 'rb').read(),
            Publish=True
        )
        logger.debug('Function updated: {0}'.format(response))
        return "done"

    def invoke_function(self, function_name, data):
        aws_lambda = boto3.client('lambda', region_name=self.default_region)
        payload = json.dumps(data)
        response = aws_lambda.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=payload,
        )
        return response['Payload'].read()

    def list_functions(self):
        aws_lambda = boto3.client('lambda', region_name=self.default_region)
        response = aws_lambda.list_functions()
        return [item['FunctionName'] for item in response['Functions']]

    def delete_function(self, function_name):
        aws_lambda = boto3.client('lambda', region_name=self.default_region)
        response = aws_lambda.delete_function(
            FunctionName=function_name
        )
        logger.debug('Function deleted: {0}'.format(response))
        return "done"

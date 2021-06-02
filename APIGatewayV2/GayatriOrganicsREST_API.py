import boto3
import json

api_gateway = boto3.client('apigateway')


def check_for_rest_api_existence(rest_api_details):
    existing_rest_apis = api_gateway.get_rest_apis()
    if existing_rest_apis:
        items = existing_rest_apis['items']
        for item in items:
            if item.get('name', '') == rest_api_details.get('name', ''):
                if rest_api_details.get('endpointConfiguration', '').get('types', '')[0] in \
                        item.get('endpointConfiguration', '').get('types', ''):
                    return item.get('id', '')
    return False


def get_resource_path(rest_api_id):
    resources = api_gateway.get_resources(restApiId=rest_api_id).get('items', {})

    resource_paths = {resource['path']: resource['id'] for resource in resources}
    return resource_paths


class RESTApiGateway:
    def __init__(self, rest_api_details):
        rest_api_id = check_for_rest_api_existence(rest_api_details)
        if not rest_api_id:
            response = api_gateway.create_rest_api(**rest_api_details)
            self.rest_api_id = response.get('id', '')
        else:
            self.rest_api_id = rest_api_id
        self.resource_path_ids = get_resource_path(self.rest_api_id)

    def create_rest_resource(self, rest_resource_details):
        try:
            response = api_gateway.create_resource(**rest_resource_details)
            self.resource_path_ids[response['path']] = response['id']
        except Exception as e:
            print(e)

    def create_method_request(self, method_details):
        try:
            api_gateway.put_method(**method_details)
        except Exception as e:
            print("method_request",e)

    def create_method_response(self, method_details):
        try:
            api_gateway.put_method_response(**method_details)
        except Exception as e:
            print("method_response",e)

    def create_integration_request(self, integration_details):
        try:
            api_gateway.put_integration(**integration_details)
        except Exception as e:
            print("integration_request",e)

    def create_integration_response(self, integration_response_details):
        try:
            api_gateway.put_integration_response(**integration_response_details)
        except Exception as e:
            print("integration_response",e)

    def deploy(self,deploy_details):
        try:
            api_gateway.create_deployment(**deploy_details)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    uri = 'arn:aws:apigateway:ap-south-1:dynamodb:action/{}'
    credentials = 'arn:aws:iam::980367155655:role/api_gateway_dynamodb'
    table_name = 'GayatriOrganicStores'

    # Creating rest_api SriGayatriOrganicsNew
    rest_api_creation_details = {
        'name': 'SriGayatriOrganicsNew',
        'description': "This api is for testing purposes",
        'version': 'v1',
        'endpointConfiguration': {'types': ['REGIONAL']}
    }
    rest_api_gateway = RESTApiGateway(rest_api_creation_details)

    sri_gayatri_organic_stores = dict()

    # Creating resource /srigayatriorganicstores
    path = '/srigayatriorganicstores'
    sri_gayatri_organic_stores[path] = {
        'restApiId': rest_api_gateway.rest_api_id,
        'parentId': rest_api_gateway.resource_path_ids['/'],
        'pathPart': 'srigayatriorganicstores'
    }
    rest_api_gateway.create_rest_resource(sri_gayatri_organic_stores[path])

    # Creating methods in /srigayatriorganicstores

    # Creating GET method_request
    sri_gayatri_organic_stores[path]['GET'] = {"method_request": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'authorizationType': 'NONE'
    }}
    rest_api_gateway.create_method_request(sri_gayatri_organic_stores.get
                                           (path).get('GET').get('method_request'))

    # Creating GET method_response
    sri_gayatri_organic_stores[path]['GET'] = {"method_response": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'statusCode': '200'
    }}
    rest_api_gateway.create_method_response(sri_gayatri_organic_stores.get
                                            (path).get('GET').get('method_response'))

    # Creating GET integration_request
    sri_gayatri_organic_stores[path]['GET'] = {"integration_request": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'type': 'AWS',
        'integrationHttpMethod': 'POST',
        'uri': uri.format('Scan'),
        'credentials': credentials,
        'requestTemplates': {'application/json': json.dumps({
            'TableName': table_name,
            'ProjectionExpression': "StorePlace,StoreID"}
        )}
    }}
    rest_api_gateway.create_integration_request(
        sri_gayatri_organic_stores.get(path).get('GET').get('integration_request'))

    # Creating GET integration_response
    sri_gayatri_organic_stores[path]['GET'] = {"integration_response": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'statusCode': '200',
        'responseTemplates': {'application/json': ''}
    }}
    rest_api_gateway.create_integration_response(
        sri_gayatri_organic_stores.get(path).get('GET').get('integration_response'))

    # Creating sub resource /srigayatriorganicstores/{storeplace}
    path = '/srigayatriorganicstores/{storeplace}'
    sri_gayatri_organic_stores[path] = {
        'restApiId': rest_api_gateway.rest_api_id,
        'parentId': rest_api_gateway.resource_path_ids['/srigayatriorganicstores'],
        'pathPart': '{storeplace}'
    }
    rest_api_gateway.create_rest_resource(sri_gayatri_organic_stores[path])

    # Creating methods in /srigayatriorganicstores/{storeplace}

    # Creating GET method_request
    sri_gayatri_organic_stores[path]['GET'] = {"method_request": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'authorizationType': 'NONE'
    }}
    rest_api_gateway.create_method_request(sri_gayatri_organic_stores.get(path).get('GET').get('method_request'))

    # Creating GET method_response
    sri_gayatri_organic_stores[path]['GET'] = {"method_response": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'statusCode': '200'
    }}
    rest_api_gateway.create_method_response(sri_gayatri_organic_stores.get
                                            (path).get('GET').get('method_response'))

    # Creating GET integration_request
    sri_gayatri_organic_stores[path]['GET'] = {"integration_request": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'type': 'AWS',
        'integrationHttpMethod': 'POST',
        'uri': uri.format('Scan'),
        'credentials': credentials,
        'requestTemplates': {'application/json': json.dumps({
            'TableName': table_name,
            'FilterExpression':'StorePlace= :storeplace',
            'ExpressionAttributeValues': {
                ':storeplace': {"S": "$input.params('storeplace')"}
            }
        }
        )}
    }}
    rest_api_gateway.create_integration_request(
        sri_gayatri_organic_stores.get(path).get('GET').get('integration_request'))

    # Creating GET integration_response
    sri_gayatri_organic_stores[path]['GET'] = {"integration_response": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'statusCode': '200',
        'responseTemplates': {'application/json': ''}
    }}
    rest_api_gateway.create_integration_response(
        sri_gayatri_organic_stores.get(path).get('GET').get('integration_response'))

    # Creating sub resource /srigayatriorganicstores/{storeplace}/{storeid}
    path = '/srigayatriorganicstores/{storeplace}/{storeid}'
    sri_gayatri_organic_stores[path] = {
        'restApiId': rest_api_gateway.rest_api_id,
        'parentId': rest_api_gateway.resource_path_ids['/srigayatriorganicstores/{storeplace}'],
        'pathPart': '{storeid}'
    }
    rest_api_gateway.create_rest_resource(sri_gayatri_organic_stores[path])

    # Creating methods in /srigayatriorganicstores/{storeplace}/{storeid}

    # Creating GET method_request
    sri_gayatri_organic_stores[path]['GET'] = {"method_request": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'authorizationType': 'NONE'
    }}
    rest_api_gateway.create_method_request(sri_gayatri_organic_stores.get(path).get('GET').get('method_request'))

    # Creating GET method_response
    sri_gayatri_organic_stores[path]['GET'] = {"method_response": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'statusCode': '200'
    }}
    rest_api_gateway.create_method_response(sri_gayatri_organic_stores.get(path).get('GET').get('method_response'))

    # Creating GET integration_request
    sri_gayatri_organic_stores[path]['GET'] = {"integration_request": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'type': 'AWS',
        'integrationHttpMethod': 'POST',
        'uri': uri.format('Scan'),
        'credentials': credentials,
        'requestTemplates': {'application/json': json.dumps({
            'TableName': table_name,
            'FilterExpression':'StorePlace= :storeplace and StoreID= :storeid',
            'ExpressionAttributeValues': {
                ':storeplace': {"S": "$input.params('storeplace')"},
                ':storeid': {"N": "$input.params('storeid')"}
            }
        }
        )}
    }}
    rest_api_gateway.create_integration_request(
        sri_gayatri_organic_stores.get(path).get('GET').get('integration_request'))

    # Creating GET integration_response
    sri_gayatri_organic_stores[path]['GET'] = {"integration_response": {
        'restApiId': rest_api_gateway.rest_api_id,
        'resourceId': rest_api_gateway.resource_path_ids[path],
        'httpMethod': 'GET',
        'statusCode': '200',
        'responseTemplates': {'application/json': ''}
    }}
    rest_api_gateway.create_integration_response(
        sri_gayatri_organic_stores.get(path).get('GET').get('integration_response'))

    # Create deployment
    sri_gayatri_organic_stores['deployment_details'] = {
        'restApiId': rest_api_gateway.rest_api_id,
        'stageName': 'test',
        'stageDescription': 'This is for testing purpose'
    }
    rest_api_gateway.deploy(sri_gayatri_organic_stores['deployment_details'])


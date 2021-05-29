"""
CREATE
READ
1. Reading specific item
2. Reading all the items
UPDATE
DELETE
"""

import boto3
from boto3.dynamodb.types import TypeDeserializer,TypeSerializer


def convert_to_dynamodb_format(data):
    serializer = TypeSerializer()
    return serializer.serialize(data)


def convert_to_python_format(data):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in data}


def read_specific_item(table, key, attributes=None):
    """Reads specific item from table"""
    if attributes is None:
        attributes = []
    dynamodb = boto3.client('dynamodb')
    response = {}
    if not attributes:
        response = dynamodb.get_item(TableName=table, Key=convert_to_dynamodb_format(key)['M'])
    else:
        response = dynamodb.get_item(TableName=table, Key=convert_to_dynamodb_format(key)['M'],
                                     ProjectionExpression=",".join(attributes))
    return convert_to_python_format(response.get('Item').items())


def read_all_the_items(table, key, attributes=None):
    """Reads all the items from the table"""
    if attributes is None:
        attributes = []

    if attributes:
        request_items = {table:{'Keys':[convert_to_dynamodb_format(key)['M']],
                                'ProjectionExpression':",".join(attributes)}}
    else:
        request_items = {table: {'Keys': [convert_to_dynamodb_format(key)['M']]}}

    dynamodb = boto3.client('dynamodb')
    response = dynamodb.batch_get_item(RequestItems=request_items)

    return [convert_to_python_format(item.items()) for item in response.get('Responses').get(table)]


if __name__ == '__main__':
    table_name = 'GayatriOrganicStores'

    # read_specific_item
    read_specific_item_key_args = {'StorePlace': 'Gopalapuram', 'StoreID': 1}
    read_specific_item_attribute_args = ['Products','Employees']
    # print(read_specific_item(table_name, read_specific_item_key_args, read_specific_item_attribute_args))
    # print(read_specific_item(table_name, read_specific_item_key_args))

    # read_all_the_items
    read_all_the_items_key_args = {'StorePlace': 'Gopalapuram','StoreID':1}
    read_all_the_items_attribute_args = ['Employees']
    print(read_all_the_items(table_name,read_all_the_items_key_args))
    print(read_all_the_items(table_name,read_all_the_items_key_args,read_all_the_items_attribute_args))

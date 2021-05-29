"""
CREATE
READ
1. Reading specific item
2. Reading all the items
UPDATE
DELETE
"""

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


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


def read_all_the_items_batch_get_item(table, key, attributes=None):
    """Reads all the items from the table using batch_get_item"""
    if attributes is None:
        attributes = []

    if attributes:
        request_items = {table: {'Keys': [convert_to_dynamodb_format(key)['M']],
                                 'ProjectionExpression': ",".join(attributes)}}
    else:
        request_items = {table: {'Keys': [convert_to_dynamodb_format(key)['M']]}}

    dynamodb = boto3.client('dynamodb')
    # This is useful when it has only partition key. (not sort key)
    response = dynamodb.batch_get_item(RequestItems=request_items)

    return [convert_to_python_format(item.items()) for item in response.get('Responses').get(table)]


def read_all_the_items_scan(table, attributes=None, filter_condition=None, attribute_names=None,
                            attribute_values=None):
    """Reads all the items from the table using batch_get_item"""
    if attribute_names is None:
        attribute_names = {}
    if attribute_values is None:
        attribute_values = {}
    if filter_condition is None:
        filter_condition = []
    if attributes is None:
        attributes = []

    dynamodb = boto3.client('dynamodb')

    if attributes and filter_condition and attribute_names and attribute_values:
        response = dynamodb.scan(TableName=table, ProjectionExpression=",".join(attributes),
                                 FilterExpression=" and ".join(filter_condition),
                                 ExpressionAttributeNames=attribute_names,
                                 ExpressionAttributeValues=attribute_values)

    elif attributes and filter_condition and attribute_names:
        response = dynamodb.scan(TableName=table, ProjectionExpression=",".join(attributes),
                                 FilterExpression=" and ".join(filter_condition),
                                 ExpressionAttributeNames=attribute_names)

    elif attributes and filter_condition and attribute_values:
        response = dynamodb.scan(TableName=table, ProjectionExpression=",".join(attributes),
                                 FilterExpression=" and ".join(filter_condition),
                                 ExpressionAttributeValues=attribute_values)

    elif attributes and filter_condition:
        response = dynamodb.scan(TableName=table, ProjectionExpression=",".join(attributes),
                                 FilterExpression=" and ".join(filter_condition))

    elif attributes and attribute_names:
        response = dynamodb.scan(TableName=table, ProjectionExpression=",".join(attributes),
                                 ExpressionAttributeNames=attribute_names)

    elif attributes:
        response = dynamodb.scan(TableName=table, ProjectionExpression=",".join(attributes))

    elif filter_condition:
        response = dynamodb.scan(TableName=table, FilterExpression=" and ".join(filter_condition))

    else:
        response = dynamodb.scan(TableName=table)

    return [convert_to_python_format(item.items()) for item in response.get('Items')]


if __name__ == '__main__':
    table_name = 'GayatriOrganicStores'

    # read_specific_item
    read_specific_item_key_args = {'StorePlace': 'Gopalapuram', 'StoreID': 1}
    read_specific_item_attribute_args = ['Products', 'Employees']
    data1 = read_specific_item(table_name, read_specific_item_key_args, read_specific_item_attribute_args)
    print(data1)
    data2 = read_specific_item(table_name, read_specific_item_key_args)
    print(data2)

    # read_all_the_items_batch_get_item - not useful if table has both partition key and sort key
    read_all_the_items_key_args = {'StorePlace': 'Gopalapuram', 'StoreID': 1}
    read_all_the_items_attribute_args = ['Employees']
    data3 = read_all_the_items_batch_get_item(table_name, read_all_the_items_key_args)
    print(data3)
    data4 = read_all_the_items_batch_get_item(table_name, read_all_the_items_key_args,
                                              read_all_the_items_attribute_args)
    print(data4)

    # read_all_the_items_scan
    # arguments - table
    data5 = read_all_the_items_scan(table_name)
    print(data5)

    # arguments - table,filter_condition
    read_all_the_items_scan_filter_args = ['attribute_exists(Employees.E5)']
    data6 = read_all_the_items_scan(table_name, filter_condition=read_all_the_items_scan_filter_args)
    print(data6)

    # arguments - table,attributes
    read_all_the_items_scan_attributes_args = ['StorePlace', 'StoreID', 'Employees']
    data7 = read_all_the_items_scan(table_name, attributes=read_all_the_items_scan_attributes_args)
    print(data7)

    # arguments - table,attributes,attribute_names
    read_all_the_items_scan_attributes_args = ['Employees.#id', 'Employees.#id1']
    read_all_the_items_scan_attribute_names_args = {'#id': '2', '#id1': 'E5'}
    data8 = read_all_the_items_scan(table_name, attributes=read_all_the_items_scan_attributes_args,
                                    attribute_names=read_all_the_items_scan_attribute_names_args)
    print(data8)

    # arguments - table,attributes,filter_condition
    read_all_the_items_scan_attributes_args = ['StorePlace', 'StoreID', 'Employees']
    read_all_the_items_scan_filter_args = ['attribute_exists(Employees.E5)']
    data9 = read_all_the_items_scan(table_name, attributes=read_all_the_items_scan_attributes_args,
                                    filter_condition=read_all_the_items_scan_filter_args)
    print(data9)

    # arguments = table,attributes,filter_condition,attribute_values
    read_all_the_items_scan_attribute_args = ['StorePlace', 'StoreID', 'Employees']
    read_all_the_items_scan_filter_args = ['StoreID= :id', 'StorePlace= :place']
    read_all_the_items_scan_attribute_value_args = convert_to_dynamodb_format({':id': 1, ':place': 'Tanuku'})['M']
    data10 = read_all_the_items_scan(table_name, attributes=read_all_the_items_scan_attribute_args,
                                     filter_condition=read_all_the_items_scan_filter_args,
                                     attribute_values=read_all_the_items_scan_attribute_value_args)
    print(data10)

    # arguments = table,attributes,filter_condition,attribute_names
    read_all_the_items_scan_attribute_args = ['StorePlace', 'StoreID', 'Employees']
    read_all_the_items_scan_filter_args = ['attribute_exists(Employees.#newid)']
    read_all_the_items_scan_attribute_names_args = {"#newid": '2'}
    data11 = read_all_the_items_scan(table_name, attributes=read_all_the_items_scan_attribute_args,
                                     filter_condition=read_all_the_items_scan_filter_args,
                                     attribute_names=read_all_the_items_scan_attribute_names_args)
    print(data11)

    # arguments = table,attributes,filter_condition,attribute_names
    read_all_the_items_scan_attribute_args = ['StorePlace', 'StoreID', 'Employees']
    read_all_the_items_scan_filter_args = ['contains(Employees.#newid.#Name,:name)']
    read_all_the_items_scan_attribute_names_args = {"#newid": '1', '#Name': 'Name'}
    read_all_the_items_scan_attribute_values_args = convert_to_dynamodb_format({':name': 'Tata Reddy'})['M']
    data12 = read_all_the_items_scan(table_name, attributes=read_all_the_items_scan_attribute_args,
                                     filter_condition=read_all_the_items_scan_filter_args,
                                     attribute_names=read_all_the_items_scan_attribute_names_args,
                                     attribute_values=read_all_the_items_scan_attribute_values_args)
    print(data12)

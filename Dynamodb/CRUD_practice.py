"""
CREATE
READ
1. Reading specific item
2. Reading all the items
UPDATE
1. Adding new employee to store
2. Adding new Product to store
3. Adding new Product in all stores
4. Increasing quantity for particular prodcut in particular store.
5. Increasing quantity for particular product in all stores.
6. Decreasing quantity for particular product in particular store.
DELETE
"""

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import botocore


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


def read_using_execute_statement(statement, parameters=None):
    if parameters is None:
        parameters = {}

    dynamodb = boto3.client('dynamodb')

    response = {}

    if statement and parameters:
        response = dynamodb.execute_statement(Statement=statement, Parameters=parameters)
    elif statement:
        response = dynamodb.execute_statement(Statement=statement)
    return response


def update_using_update_item(table_name, key, update_expression, condition_expression=None, exp_attribute_names=None,
                             exp_attribute_values=None):
    if exp_attribute_values is None:
        exp_attribute_values = []
    if exp_attribute_names is None:
        exp_attribute_names = {}
    if condition_expression is None:
        condition_expression = []

    dynamodb = boto3.client('dynamodb')

    if condition_expression and exp_attribute_names and exp_attribute_values:
        response = dynamodb.update_item(TableName=table_name, Key=key,
                                        UpdateExpression=update_expression,
                                        ConditionExpression=condition_expression,
                                        ExpressionAttributeNames=exp_attribute_names,
                                        ExpressionAttributeValues=exp_attribute_values)

    elif condition_expression and exp_attribute_names:
        response = dynamodb.update_item(TableName=table_name, Key=key,
                                        UpdateExpression=update_expression,
                                        ConditionExpression=condition_expression,
                                        ExpressionAttributeNames=exp_attribute_names)

    elif condition_expression and exp_attribute_values:
        response = dynamodb.update_item(TableName=table_name, Key=key,
                                        UpdateExpression=update_expression,
                                        ConditionExpression=condition_expression,
                                        ExpressionAttributeValues=exp_attribute_values)

    elif exp_attribute_names and exp_attribute_values:
        response = dynamodb.update_item(TableName=table_name, Key=key,
                                        UpdateExpression=update_expression,
                                        ExpressionAttributeNames=exp_attribute_names,
                                        ExpressionAttributeValues=exp_attribute_values)

    elif exp_attribute_names:
        response = dynamodb.update_item(TableName=table_name, Key=key,
                                        UpdateExpression=update_expression,
                                        ExpressionAttributeNames=exp_attribute_names)

    elif exp_attribute_values:
        response = dynamodb.update_item(TableName=table_name, Key=key,
                                        UpdateExpression=update_expression,
                                        ExpressionAttributeValues=exp_attribute_values)

    else:
        response = dynamodb.update_item(TableName=table_name, Key=key, UpdateExpression=update_expression)
    return response


def read_practice():
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
    read_all_the_items_scan_filter_args = ['attribute_exists(Products.P24)']
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
    read_all_the_items_scan_filter_args = ['attribute_exists(Products.P5)']
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

    read_using_execute_statement_partiql_string = "select StorePlace,StoreID,Employees from GayatriOrganicStores" \
                                                  " where StorePlace=? and StoreID=?"
    read_using_execute_statement_partiql_params = [{'S': 'Bhimavaram'}, {'N': '1'}, {'S': '15'}]
    data13 = read_using_execute_statement(read_using_execute_statement_partiql_string,
                                          read_using_execute_statement_partiql_params)
    print(data13)


def update_practice():

    table = "GayatriOrganicStores"

    # Adding new employee to a particular store
    update_using_update_item_key_args = convert_to_dynamodb_format({'StorePlace': 'Bhimavaram', 'StoreID': 2})['M']
    update_using_update_item_update_expression_args = "set Employees.#id = :val"
    update_using_update_item_exp_attribute_names = {'#id': '103'}
    update_using_update_item_exp_attribute_values = convert_to_dynamodb_format({':val': {'Name': 'tarunkumar',
                                                                                         'PhoneNo': '9988998899'}})['M']
    data1 = update_using_update_item(table, update_using_update_item_key_args,
                                     update_expression=update_using_update_item_update_expression_args,
                                     exp_attribute_names=update_using_update_item_exp_attribute_names,
                                     exp_attribute_values=update_using_update_item_exp_attribute_values)
    print(data1)

    # Adding new Product to particular store
    update_using_update_item_key_args = convert_to_dynamodb_format({'StorePlace': 'Gopalapuram', 'StoreID': 1})['M']
    update_using_update_item_update_expression_args = "set Products.#id = :val"
    update_using_update_item_exp_attribute_names = {'#id': 'P25'}
    update_using_update_item_exp_attribute_values = convert_to_dynamodb_format({':val': {'Name': 'Black Wheat',
                                                                                         'Category': 'Rice',
                                                                                         'Quantity': 0,
                                                                                         'Price': 0}})['M']
    data2_1 = update_using_update_item(table, update_using_update_item_key_args,
                                       update_expression=update_using_update_item_update_expression_args,
                                       exp_attribute_names=update_using_update_item_exp_attribute_names,
                                       exp_attribute_values=update_using_update_item_exp_attribute_values)
    print(data2_1)

    update_using_update_item_key_args = convert_to_dynamodb_format({'StorePlace': 'Gopalapuram', 'StoreID': 1})['M']
    update_using_update_item_update_expression_args = "set Products.#id = :val"
    update_using_update_item_exp_attribute_names = {'#id': 'P25'}
    update_using_update_item_exp_attribute_values = convert_to_dynamodb_format({':val': {'Name': 'Black Wheat',
                                                                                         'Category': 'Rice',
                                                                                         'Quantity': 20,
                                                                                         'Price': 100,
                                                                                         'Can Sell': 'Y'}})['M']
    data2_2 = update_using_update_item(table, update_using_update_item_key_args,
                                       update_expression=update_using_update_item_update_expression_args,
                                       exp_attribute_names=update_using_update_item_exp_attribute_names,
                                       exp_attribute_values=update_using_update_item_exp_attribute_values)
    print(data2_2)

    # Increasing quantity for particular product in particular store.
    update_using_update_item_key_args = convert_to_dynamodb_format({'StorePlace': 'Gopalapuram', 'StoreID': 1})['M']
    update_using_update_item_update_expression_args = "add Products.#id.Quantity :val"
    update_using_update_item_exp_attribute_names = {'#id': 'P25'}
    update_using_update_item_exp_attribute_values = convert_to_dynamodb_format({':val': 20})['M']
    data3 = update_using_update_item(table, update_using_update_item_key_args,
                                       update_expression=update_using_update_item_update_expression_args,
                                       exp_attribute_names=update_using_update_item_exp_attribute_names,
                                       exp_attribute_values=update_using_update_item_exp_attribute_values)
    print(data3)

    update_using_update_item_key_args = convert_to_dynamodb_format({'StorePlace': 'Gopalapuram', 'StoreID': 1})['M']
    update_using_update_item_update_expression_args = "add Products.#id.Quantity :val"
    update_using_update_item_exp_attribute_names = {'#id': 'P25'}
    update_using_update_item_exp_attribute_values = convert_to_dynamodb_format({':val': 20, ':cval': 100})['M']
    update_using_update_item_update_conditional_args = 'Products.#id.Quantity < :cval'
    try:
        data3_1 = update_using_update_item(table, update_using_update_item_key_args,
                                           update_expression=update_using_update_item_update_expression_args,
                                           condition_expression=update_using_update_item_update_conditional_args,
                                           exp_attribute_names=update_using_update_item_exp_attribute_names,
                                           exp_attribute_values=update_using_update_item_exp_attribute_values)
        print(data3_1)
    except Exception as e:
        print(e)

    # Decreasing quantity for particular product in particular store.
    update_using_update_item_key_args = convert_to_dynamodb_format({'StorePlace': 'Gopalapuram', 'StoreID': 1})['M']
    update_using_update_item_update_expression_args = "add Products.#id.Quantity :val"
    update_using_update_item_exp_attribute_names = {'#id': 'P25'}
    update_using_update_item_exp_attribute_values = convert_to_dynamodb_format({':val': -10})['M']
    data4 = update_using_update_item(table, update_using_update_item_key_args,
                                     update_expression=update_using_update_item_update_expression_args,
                                     exp_attribute_names=update_using_update_item_exp_attribute_names,
                                     exp_attribute_values=update_using_update_item_exp_attribute_values)
    print(data4)

    # Adding new Product in all stores
    update_using_update_item_update_expression_args = "set Products.#id = :val"
    update_using_update_item_exp_attribute_names = {'#id': 'P26'}
    update_using_update_item_exp_attribute_values = convert_to_dynamodb_format({':val': {'Name': 'Black Wheat',
                                                                                         'Category': 'Rice',
                                                                                         'Quantity': 0,
                                                                                         'Price': 0}})['M']
    update_using_update_item_update_conditional_args = 'attribute_exists(Products)'
    read_all_the_items_scan_attributes_args = ['StorePlace', 'StoreID']
    keys = read_all_the_items_scan(table, attributes=read_all_the_items_scan_attributes_args)
    for key in keys:
        try:
            update_using_update_item_key_args = convert_to_dynamodb_format(key)['M']
            data5 = update_using_update_item(table, update_using_update_item_key_args,
                                             update_expression=update_using_update_item_update_expression_args,
                                             condition_expression=update_using_update_item_update_conditional_args,
                                             exp_attribute_names=update_using_update_item_exp_attribute_names,
                                             exp_attribute_values=update_using_update_item_exp_attribute_values)
            print(key, data5)
        except Exception as e:
            print(key, e)

    # Increasing quantity for particular product in all stores.
    update_using_update_item_update_expression_args = "add Products.#id.Quantity :val"
    update_using_update_item_exp_attribute_names = {'#id': 'P26'}
    update_using_update_item_exp_attribute_values = convert_to_dynamodb_format({':val': 10})['M']
    keys = read_all_the_items_scan(table, attributes=read_all_the_items_scan_attributes_args)
    for key in keys:
        try:
            update_using_update_item_key_args = convert_to_dynamodb_format(key)['M']
            data6 = update_using_update_item(table, update_using_update_item_key_args,
                                             update_expression=update_using_update_item_update_expression_args,
                                             exp_attribute_names=update_using_update_item_exp_attribute_names,
                                             exp_attribute_values=update_using_update_item_exp_attribute_values)
            print(key, data6)
        except Exception as e:
            print(key, e)

    pass


if __name__ == '__main__':
    """
    Uncomment one by one while running.
    """
    # read_practice()
    # update_practice()

    pass

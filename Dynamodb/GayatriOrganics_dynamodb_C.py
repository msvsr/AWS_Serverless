import boto3
import random
import pandas as pd
from boto3.dynamodb.types import TypeSerializer


def modify_pandas_type(pd_obj,source,target):
    for column in pd_obj:
        if pd_obj.dtypes[column] == source:
            pd_obj[column] = pd_obj[column].astype(target)


def serialize_data_to_dynamodb(data_to_serialize):
    serializer = TypeSerializer()
    return serializer.serialize(data_to_serialize)


def get_data_from_excel(excel_filename,sheet_names):
    excel_data = {}

    for sheet_name in sheet_names:
        excel_data[sheet_name] = pd.read_excel(excel_filename,sheet_name=sheet_name)
        modify_pandas_type(excel_data[sheet_name],'object','str')

    return excel_data


def get_stores_dict_list(stores):
    stores_dict_list = []
    for index, store in stores.iterrows():
        stores_dict_list.append(serialize_data_to_dynamodb(store.to_dict())['M'])
    return stores_dict_list


def get_products_dict_list(products,no_of_stores):
    stores_products_list = []
    no_of_products = len(products.index)

    for i in range(no_of_stores):
        no_of_products_to_add = random.randint(no_of_products//2, no_of_products)
        sample_products_ids_to_add = random.sample(range(no_of_products), no_of_products_to_add)
        sample_products_to_add = products.iloc[sample_products_ids_to_add]
        columns = [column for column in sample_products_to_add.columns if column != 'ID']
        products_dict = {str(product['ID']): product[columns].to_dict() for index, product in sample_products_to_add.iterrows()}
        stores_products_list.append(serialize_data_to_dynamodb(products_dict))
    return stores_products_list


def get_employees_dict_list(employees):
    columns = [column for column in employees.columns if column != 'ID']
    employees_dict_list = [serialize_data_to_dynamodb({str(employee['ID']):employee[columns].to_dict()}) for index, employee in employees.iterrows()]
    return employees_dict_list


def get_timings_dict_list(timings):
    timings_dict_list = [serialize_data_to_dynamodb(timing.to_dict()) for index, timing in timings.iterrows()]
    return timings_dict_list


def add_stores_data_to_dynamodb(table_name, stores):
    dynamodb = boto3.client('dynamodb')
    for store in stores:
        dynamodb.put_item(TableName=table_name, Item=store)


def add_stores_products_data_to_dynamodb(table_name, stores, products):
    no_of_stores = len(stores)
    dynamodb = boto3.client('dynamodb')
    for store_no in range(no_of_stores):
        key = stores[store_no]
        update_expression = "SET Products = :products_data"
        expression_attribute_values = {':products_data': products[store_no]}
        dynamodb.update_item(TableName=table_name, Key=key, UpdateExpression=update_expression,
                             ExpressionAttributeValues=expression_attribute_values)


def add_stores_employees_data_to_dynamodb(table_name, stores, employees):
    no_of_stores = len(stores)
    dynamodb = boto3.client('dynamodb')
    for store_no in range(no_of_stores):
        key = stores[store_no]
        update_expression = "SET Employees = :employees_data"
        expression_attribute_values = {':employees_data':employees[store_no]}
        dynamodb.update_item(TableName=table_name, Key=key, UpdateExpression=update_expression,
                             ExpressionAttributeValues=expression_attribute_values)


def add_stores_timings_data_to_dynamodb(table_name, stores, timings):
    no_of_stores = len(stores)
    dynamodb = boto3.client('dynamodb')
    for store_no in range(no_of_stores):
        key = stores[store_no]
        update_expression = "SET Timings = :timings_data"
        expression_attribute_values = {':timings_data': timings[store_no]}
        dynamodb.update_item(TableName=table_name, Key=key, UpdateExpression=update_expression,
                             ExpressionAttributeValues=expression_attribute_values)


def add_stores_attributes(table_name, stores, new_data, attribute_name):
    no_of_stores = len(stores)
    dynamodb = boto3.client('dynamodb')
    for store_no in range(no_of_stores):
        key = stores[store_no]
        update_expression = "SET {} = :data".format(attribute_name)
        expression_attribute_values = {':data': new_data[store_no]}
        dynamodb.update_item(TableName=table_name, Key=key, UpdateExpression=update_expression,
                             ExpressionAttributeValues=expression_attribute_values)


if __name__ == '__main__':

    data = get_data_from_excel('GayatriOrganics.xlsx', ['Stores', 'ProductsList', 'Employees', 'Timings'])

    stores_data = get_stores_dict_list(data['Stores'])
    products_data = get_products_dict_list(data['ProductsList'],len(stores_data))
    employees_data = get_employees_dict_list(data['Employees'])
    timings_data = get_timings_dict_list(data['Timings'])

    add_stores_data_to_dynamodb('GayatriOrganicStores',stores_data)
    add_stores_attributes('GayatriOrganicStores', stores_data, products_data, "Products")
    add_stores_attributes('GayatriOrganicStores',stores_data,employees_data, "Employees")
    add_stores_attributes('GayatriOrganicStores',stores_data,timings_data, "Timings")


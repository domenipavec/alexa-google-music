import boto3

import settings


def get_table():
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
    return dynamodb.Table(settings.AWS_DYNAMODB_TABLE)


def get(user_id):
    table = get_table()
    item = table.get_item(Key={'userid': user_id})
    if 'Item' in item:
        if 'state' in item['Item']:
            return item['Item']['state']
    return {}


def save(user_id, state):
    table = get_table()
    table.put_item(Item={'userid': user_id, 'state': state})

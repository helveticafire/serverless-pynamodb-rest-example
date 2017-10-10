from http import HTTPStatus
from datetime import datetime
import json
import logging
import os
import uuid

from todos.todo_model import TodoModel
from utils.constants import ENV_VAR_ENVIRONMENT, ENV_VAR_DYNAMODB_TABLE, ENV_VAR_DYNAMODB_REGION


def handle(event, context):
    try:
        table_name = os.environ[ENV_VAR_DYNAMODB_TABLE]
        region = os.environ[ENV_VAR_DYNAMODB_REGION]
    except KeyError as err:
        return {'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                'body': json.dumps({'error': 'ENV_VAR_NOT_SET',
                                    'error_message': '{0} is missing from environment variables'.format(str(err))})}

    TodoModel.setup_model(TodoModel, region, table_name, ENV_VAR_ENVIRONMENT not in os.environ)

    try:
        data = json.loads(event['body'])
    except ValueError as err:
        return {'statusCode': HTTPStatus.BAD_REQUEST.value,
                'body': json.dumps({'error': 'JSON_IRREGULAR',
                                    'error_message': str(err)})}

    if 'text' not in data:
        logging.error('Validation Failed')
        return {'statusCode': HTTPStatus.BAD_REQUEST.value,
                'body': json.dumps({'error': 'BODY_PROPERTY_MISSING',
                                    'error_message': 'Could not create the todo item.'})}

    if not data['text']:
        logging.error('Validation Failed - text was empty. %s', data)
        return {'statusCode': HTTPStatus.BAD_REQUEST.value,
                'body': json.dumps({'error': 'VALIDATION_FAILED',
                                    'error_message': 'Could not create the todo item. As text was empty.'})}

    a_todo = TodoModel(todo_id=str(uuid.uuid1()),
                       text=data['text'],
                       checked=False,
                       created_at=datetime.now())

    # write the todo to the database
    a_todo.save()

    # create a response
    return {'statusCode': HTTPStatus.CREATED.value,
            'body': json.dumps(dict(a_todo))}


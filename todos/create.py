import json
import logging
import os
import uuid

from todos.todo_model import TodoModel


def create(event, context):
    try:
        TodoModel.Meta.table_name = os.environ['DYNAMODB_TABLE']
    except KeyError as err:
        return {'statusCode': 500,
                'body': json.dumps({'error': 'ENV_VAR_NOT_SET',
                                    'error_message': '{0} is missing from environment variables'.format(str(err))})}

    try:
        data = json.loads(event['body'])
    except ValueError as err:
        return {'statusCode': 400,
                'body': json.dumps({'error': 'JSON_IRREGULAR',
                                    'error_message': str(err)})}

    if 'text' not in data:
        logging.error('Validation Failed')
        return {'statusCode': 422,
                'body': json.dumps({'error': 'BODY_PROPERTY_MISSING',
                                    'error_message': 'Couldn\'t create the todo item.'})}

    if not data['text']:
        logging.error('Validation Failed - text was empty. %s', data)
        return {'statusCode': 422,
                'body': json.dumps({'error': 'VALIDATION_FAILED',
                                    'error_message': 'Couldn\'t create the todo item. As text was empty.'})}

    a_todo = TodoModel(todo_id=str(uuid.uuid1()),
                       text=data['text'],
                       checked=False)

    # write the todo to the database
    a_todo.save()

    # create a response
    return {'statusCode': 201,
            'body': json.dumps(dict(a_todo))}


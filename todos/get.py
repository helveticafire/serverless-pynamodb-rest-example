import json
import logging
import os

from pynamodb.exceptions import DoesNotExist

from todos.todo_model import TodoModel


def get(event, context):
    logging.warning(event)
    try:
        table_name = os.environ['DYNAMODB_TABLE']
        region = os.environ['DYNAMODB_REGION']
    except KeyError as err:
        return {'statusCode': 500,
                'body': json.dumps({'error': 'ENV_VAR_NOT_SET',
                                    'error_message': '{0} is missing from environment variables'.format(str(err))})}

    TodoModel.setup_model(TodoModel, region, table_name, 'ENV' not in os.environ)

    try:
        todo_id = event['pathParameters']['todo_id']
    except KeyError:
        return {'statusCode': 422,
                'body': json.dumps({'error': 'URL_PARAMETER_MISSING',
                                    'error_message': 'TODO id missing from url'})}

    try:
        found_todo = TodoModel.get(hash_key=todo_id)
    except DoesNotExist:
        return {'statusCode': 404,
                'body': json.dumps({'error': 'NOT_FOUND',
                                    'error_message': 'TODO was not found'})}

    # create a response
    return {'statusCode': 200,
            'body': json.dumps(dict(found_todo))}

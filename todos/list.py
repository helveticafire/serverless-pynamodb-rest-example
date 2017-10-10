from http import HTTPStatus
import json
import os

from todos.todo_model import TodoModel


def handle(event, context):
    try:
        table_name = os.environ['DYNAMODB_TABLE']
        region = os.environ['DYNAMODB_REGION']
    except KeyError as err:
        return {'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                'body': json.dumps({'error': 'ENV_VAR_NOT_SET',
                                    'error_message': '{0} is missing from environment variables'.format(str(err))})}

    TodoModel.setup_model(TodoModel, region, table_name, 'ENV' not in os.environ)

    # fetch all todos from the database
    results = TodoModel.scan()

    # create a response
    return {'statusCode': HTTPStatus.OK.value,
            'body': json.dumps({'items': [dict(result) for result in results]})}

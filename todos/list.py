from http import HTTPStatus
import json
import os

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

    # fetch all todos from the database
    results = TodoModel.scan()

    # create a response
    return {'statusCode': HTTPStatus.OK.value,
            'body': json.dumps({'items': [dict(result) for result in results]})}

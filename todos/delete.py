from http import HTTPStatus
import json
import os

from pynamodb.exceptions import DoesNotExist, DeleteError

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
        todo_id = event['pathParameters']['todo_id']
    except KeyError:
        return {'statusCode': HTTPStatus.BAD_REQUEST.value,
                'body': json.dumps({'error': 'URL_PARAMETER_MISSING',
                                    'error_message': 'TODO id missing from url'})}
    try:
        found_todo = TodoModel.get(hash_key=todo_id)
    except DoesNotExist:
        return {'statusCode': HTTPStatus.NOT_FOUND.value,
                'body': json.dumps({'error': 'NOT_FOUND',
                                    'error_message': 'TODO was not found'})}
    try:
        found_todo.delete()
    except DeleteError:
        return {'statusCode': HTTPStatus.BAD_REQUEST.value,
                'body': json.dumps({'error': 'DELETE_FAILED',
                                    'error_message': 'Unable to delete the TODO'})}

    # create a response
    return {'statusCode': HTTPStatus.NO_CONTENT.value}

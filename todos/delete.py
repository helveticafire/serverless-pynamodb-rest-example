import os

from pynamodb.exceptions import DoesNotExist, DeleteError
from todos.endpoint_schemas import SCHEMA_PATH, validate

from todos.lambda_responses import HttpNoContentResponse, HttpResponseNotFound, HttpResponseBadRequest, \
    HttpResponseServerError
from todos.todo_model import TodoModel
from utils.constants import ENV_VAR_ENVIRONMENT, ENV_VAR_DYNAMODB_TABLE, ENV_VAR_DYNAMODB_REGION


def handle(event, context):
    try:
        table_name = os.environ[ENV_VAR_DYNAMODB_TABLE]
        region = os.environ[ENV_VAR_DYNAMODB_REGION]
    except KeyError as err:
        error_message = '{0} is missing from environment variables'.format(str(err))
        return HttpResponseServerError(error_code='ENV_VAR_NOT_SET',
                                       error_message=error_message).__dict__()

    validation_result = validate(event, SCHEMA_PATH, 'Path parameters are incorrect')
    if validation_result:
        return validation_result

    todo_id = event['pathParameters']['todo_id']

    TodoModel.setup_model(TodoModel, region, table_name, ENV_VAR_ENVIRONMENT not in os.environ)

    try:
        found_todo = TodoModel.get(hash_key=todo_id)
    except DoesNotExist:
        return HttpResponseNotFound(error_message='TODO was not found').__dict__()

    try:
        found_todo.delete()
    except DeleteError:
        return HttpResponseBadRequest(error_code='DELETE_FAILED',
                                      error_message='Unable to delete the TODO').__dict__()

    # create a response
    return HttpNoContentResponse().__dict__()

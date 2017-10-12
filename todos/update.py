import json
import logging
import os

from pynamodb.exceptions import DoesNotExist

from todos.lambda_responses import HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound, \
    HttpOkJSONResponse
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

    TodoModel.setup_model(TodoModel, region, table_name, ENV_VAR_ENVIRONMENT not in os.environ)

    try:
        todo_id = event['pathParameters']['todo_id']
    except KeyError:
        return HttpResponseBadRequest(error_code='URL_PARAMETER_MISSING',
                                      error_message='TODO id missing from url').__dict__()
    try:
        found_todo = TodoModel.get(hash_key=todo_id)
    except DoesNotExist:
        return HttpResponseNotFound(error_message='TODO was not found').__dict__()

    try:
        data = json.loads(event['body'])
    except ValueError as err:
        return HttpResponseBadRequest(error_code='JSON_IRREGULAR',
                                      error_message=str(err)).__dict__()

    if 'text' not in data and 'checked' not in data:
        logging.error('Validation Failed %s', data)
        return HttpResponseBadRequest(error_code='VALIDATION_FAILED',
                                      error_message='Could not update the todo item.').__dict__()

    text_attr_changed = 'text' in data and data['text'] != found_todo.text
    if text_attr_changed:
        found_todo.text = data['text']
    checked_attr_changed = 'checked' in data and data['checked'] != found_todo.checked
    if checked_attr_changed:
        found_todo.checked = data['checked']

    if text_attr_changed or checked_attr_changed:
        found_todo.save()
    else:
        logging.info('Nothing changed did not update')

    # create a response
    return HttpOkJSONResponse(body=dict(found_todo)).__dict__()

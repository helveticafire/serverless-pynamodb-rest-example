import json
import logging
import os

from pynamodb.exceptions import DoesNotExist
from todos.endpoint_schemas import SCHEMA_UPDATE_BODY, validate, SCHEMA_PATH

from todos.lambda_responses import HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound, \
    HttpOkJSONResponse
from todos.todo_model import TodoModel
from utils.utils import dict_raise_on_duplicates
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

    try:
        data = json.loads(event['body'], object_pairs_hook=dict_raise_on_duplicates)
    except ValueError as err:
        return HttpResponseBadRequest(error_code='JSON_IRREGULAR',
                                      error_message=str(err)).__dict__()

    validation_result = validate(event, SCHEMA_UPDATE_BODY,
                                 'Please check the validation violation made trying to update a Todo and retry.')
    if validation_result:
        return validation_result

    TodoModel.setup_model(TodoModel, region, table_name, ENV_VAR_ENVIRONMENT not in os.environ)

    try:
        found_todo = TodoModel.get(hash_key=todo_id)
    except DoesNotExist:
        return HttpResponseNotFound(error_message='TODO was not found').__dict__()

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

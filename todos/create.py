from datetime import datetime
import json
import logging
import os
import uuid

from todos.lambda_responses import HttpResponseServerError, HttpResponseBadRequest, HttpCreatedJSONResponse
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
        data = json.loads(event['body'])
    except ValueError as err:
        return HttpResponseBadRequest(error_code='JSON_IRREGULAR',
                                      error_message=str(err)).__dict__()

    if 'text' not in data:
        logging.error('Validation Failed')
        return HttpResponseBadRequest(error_code='BODY_PROPERTY_MISSING',
                                      error_message='Could not create the todo item.').__dict__()

    if not data['text']:
        logging.error('Validation Failed - text was empty. %s', data)
        return HttpResponseBadRequest(error_code='VALIDATION_FAILED',
                                      error_message='Could not create the todo item. As text was empty.').__dict__()

    a_todo = TodoModel(todo_id=str(uuid.uuid1()),
                       text=data['text'],
                       checked=False,
                       created_at=datetime.now())

    # write the todo to the database
    a_todo.save()

    # create a response
    return HttpCreatedJSONResponse(body=dict(a_todo)).__dict__()

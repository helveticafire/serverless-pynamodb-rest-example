import json
import logging
import os

from pynamodb.exceptions import DoesNotExist

from todos.todo_model import TodoModel


def handle(event, context):
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

    try:
        data = json.loads(event['body'])
    except ValueError as err:
        return {'statusCode': 400,
                'body': json.dumps({'error': 'JSON_IRREGULAR',
                                    'error_message': str(err)})}

    if 'text' not in data and 'checked' not in data:
        logging.error('Validation Failed %s', data)
        return {'statusCode': 422,
                'body': json.dumps({'error': 'VALIDATION_FAILED',
                                    'error_message': 'Couldn\'t update the todo item.'})}

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
    return {'statusCode': 200,
            'body': json.dumps(dict(found_todo))}

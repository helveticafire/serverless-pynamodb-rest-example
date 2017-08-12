import json
import os

from todos.todo_model import TodoModel


def todo_list(event, context):
    try:
        TodoModel.Meta.table_name = os.environ['DYNAMODB_TABLE']
    except KeyError as err:
        return {'statusCode': 500,
                'body': json.dumps({'error': 'ENV_VAR_NOT_SET',
                                    'error_message': '{0} is missing from environment variables'.format(str(err))})}

    # fetch all todos from the database
    results = TodoModel.scan()

    # create a response
    return {'statusCode': 200,
            'body': json.dumps({'items': [dict(result) for result in results]})}

# import logging
from jsonschema import Draft4Validator
from todos.lambda_responses import HttpErrorValidationFailed

BODY_PROPERTIES = {'text': {'id': '/properties/text', 'minLength': 1, 'type': 'string'},
                   'checked': {'id': '/properties/checked', 'type': 'boolean'}}

SCHEMA_CREATE_BODY = {
    'properties': BODY_PROPERTIES,
    'required': [
        'text'
    ],
    'type': 'object'
}

SCHEMA_UPDATE_BODY = {
    'properties': BODY_PROPERTIES,
    "anyOf": [
        {"required": ["checked"]},
        {"required": ["text"]},
    ],
    'type': 'object'
}

SCHEMA_PATH = {
    'properties': {
        'pathParameters': {
            'id': '/properties/pathParameters',
            'properties': {
                'todo_id': {
                    'id': '/properties/pathParameters/properties/todo_id',
                    'minLength': 32,
                    'maxLength': 32,
                    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
                    'type': 'string'
                }
            },
            'required': [
                'todo_id'
            ],
            'type': 'object'
        }
    },
    'required': [
        'pathParameters'
    ],
    'type': 'object'
}


def validate(data, schema, error_message):
    validator = Draft4Validator(schema)

    validation_violations = []
    for error in sorted(validator.iter_errors(data), key=str):
        validation_violations.append({'message': error.message,
                                      'original_value': error.instance})

    if not validation_violations:
        return None

    # logging.error('Validation Failed')
    # error_message = 'Please check the validation violation made trying to make a Todo and retry.'
    return HttpErrorValidationFailed(error_message=error_message,
                                     validation_violations=validation_violations).__dict__()

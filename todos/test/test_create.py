import json
from unittest import TestCase

import mock

from todos.create import create


@mock.patch('todos.create.TodoModel')
class TestCreateEnvVar(TestCase):
    @mock.patch('os.environ', {})
    def test_env_missing_all_vars(self, _):
        context_mock = mock.MagicMock(function_name='create', aws_request_id='123')
        response = create({}, context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('ENV_VAR_NOT_SET', body_json['error'])
        self.assertEquals('\'DYNAMODB_TABLE\' is missing from environment variables', body_json['error_message'])
        self.assertEqual(response['statusCode'], 500)


@mock.patch('todos.create.TodoModel')
@mock.patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                           'DYNAMODB_REGION': 'eu-central-1'})
class TestCreate(TestCase):
    def setUp(self):
        self.context_mock = mock.MagicMock(function_name='create', aws_request_id='123')
        super(TestCreate, self).setUp()

    def test_bad_json(self, _):
        response = create({'body': ''}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('JSON_IRREGULAR', body_json['error'])
        self.assertEquals('No JSON object could be decoded', body_json['error_message'])
        self.assertEqual(response['statusCode'], 400)

    def test_text_missing_from_body(self, _):
        with mock.patch('todos.create.logging.error'):
            response = create({'body': '{}'}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('BODY_PROPERTY_MISSING', body_json['error'])
        self.assertEquals('Couldn\'t create the todo item.', body_json['error_message'])
        self.assertEqual(response['statusCode'], 422)

    def test_text_value_empty(self, _):
        with mock.patch('todos.create.logging.error'):
            response = create({'body': '{"text": ""}'}, self.context_mock)
            body_json = json.loads(response['body'])
            self.assertEquals('VALIDATION_FAILED', body_json['error'])
            self.assertEquals('Couldn\'t create the todo item. As text was empty.', body_json['error_message'])
            self.assertEqual(response['statusCode'], 422)

    def test_create(self, mock_model):
        with mock.patch('uuid.uuid1', return_value='3f248497-7fa5-11e7-a657-e0accb8996e6') as mock_id:
            created_todo = mock.MagicMock(text='blah', todo_id=mock_id)
            mock_model.return_value = created_todo
            response = create({'body': '{"text": "blah"}'}, self.context_mock)
            body_json = json.loads(response['body'])
            # TODO: figure out why this is not working. -
            created_todo.save.assert_called()
            # TODO: Test response is correct
            self.assertEquals('error' in body_json, False)
            self.assertEquals('error_message' in body_json, False)
            self.assertEqual(response['statusCode'], 201)

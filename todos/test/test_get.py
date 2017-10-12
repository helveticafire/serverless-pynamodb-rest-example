import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from pynamodb.exceptions import DoesNotExist

from todos.get import handle
from todos.test.test_todo_model_integration import TestIntegrationBase


@patch('todos.get.TodoModel')
@patch('os.environ', {})
class TestGetEnvVar(TestCase):
    def test_env_missing_vars(self, _):
        context_mock = MagicMock(function_name='get', aws_request_id='123')
        response = handle({}, context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('ENV_VAR_NOT_SET', body_json['error_code'])
        self.assertEquals('\'DYNAMODB_TABLE\' is missing from environment variables', body_json['error_message'])
        self.assertEqual(response['statusCode'], 500)


@patch('todos.get.TodoModel')
@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
class TestGet(TestCase):
    def setUp(self):
        self.context_mock = MagicMock(function_name='get', aws_request_id='123')
        super().setUp()

    def test_path_param_missing(self, _):
        response = handle({}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('URL_PARAMETER_MISSING', body_json['error_code'])
        self.assertEquals('TODO id missing from url', body_json['error_message'])
        self.assertEqual(response['statusCode'], 400)

    def test_todo_not_found(self, mock_model):
        mock_model.get.side_effect = DoesNotExist()
        response = handle({'pathParameters': {'todo_id': '1'}}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('NOT_FOUND', body_json['error_code'])
        self.assertEquals('TODO was not found', body_json['error_message'])
        self.assertEqual(response['statusCode'], 404)

    def test_successfully(self, mock_model):
        todo_item = {'todo_id': '1', 'text': 'hello'}
        mock_model.get.return_value = todo_item

        response = handle({'pathParameters': {'todo_id': '1'}}, self.context_mock)
        mock_model.get.assert_called_once_with(hash_key='1')
        body_json = json.loads(response['body'])
        self.assertEquals('error_code' in body_json, False)
        self.assertEquals('error_message' in body_json, False)
        self.assertEquals(body_json, todo_item)
        self.assertEqual(response['statusCode'], 200)


@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
class TestGetIntegration(TestIntegrationBase):
    def setUp(self, load_dbs=None):
        self.context_mock = MagicMock(function_name='get', aws_request_id='123')
        super().setUp(load_dbs=[os.path.join(self.dir_path, 'fixtures/todo_db_0.json')])

    def test_get(self):
        response = handle({'pathParameters': {'todo_id': 'd490d766-8b60-11e7-adba-e0accb8996e6'}}, self.context_mock)
        self.assertEqual(response['statusCode'], 200)
        body_json = json.loads(response['body'])
        self.assertDictEqual(body_json, {'checked': False,
                                         'created_at': '2017-08-27T21:49:25.310975+0000',
                                         'text': 'text of d490d766-8b60-11e7-adba-e0accb8996e6',
                                         'todo_id': 'd490d766-8b60-11e7-adba-e0accb8996e6',
                                         'updated_at': '2017-08-27T21:49:25.779499+0000'})

    def test_get_failed(self):
        response = handle({'pathParameters': {'todo_id': 'd490d766-8b60-11e7-adba-e0accb8996e6a'}}, self.context_mock)
        self.assertEqual(response['statusCode'], 404)
        body_json = json.loads(response['body'])
        self.assertEquals('error_code' in body_json, True)
        self.assertEquals(body_json['error_code'], 'NOT_FOUND')
        self.assertEquals(body_json['error_message'], 'TODO was not found')

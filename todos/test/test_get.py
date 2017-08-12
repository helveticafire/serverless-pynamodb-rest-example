import json
from unittest import TestCase

from mock import mock
from pynamodb.exceptions import DoesNotExist

from todos.get import get


@mock.patch('todos.get.TodoModel')
@mock.patch('os.environ', {})
class TestGetEnvVar(TestCase):
    def test_env_missing_vars(self, _):
        context_mock = mock.MagicMock(function_name='get', aws_request_id='123')
        response = get({}, context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('ENV_VAR_NOT_SET', body_json['error'])
        self.assertEquals('\'DYNAMODB_TABLE\' is missing from environment variables', body_json['error_message'])
        self.assertEqual(response['statusCode'], 500)


@mock.patch('todos.get.TodoModel')
@mock.patch('os.environ', {'DYNAMODB_TABLE': 'todo_table'})
class TestGet(TestCase):
    def setUp(self):
        self.context_mock = mock.MagicMock(function_name='get', aws_request_id='123')
        super(TestGet, self).setUp()

    def test_path_param_missing(self, _):
        response = get({}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('URL_PARAMETER_MISSING', body_json['error'])
        self.assertEquals('TODO id missing from url', body_json['error_message'])
        self.assertEqual(response['statusCode'], 422)

    def test_todo_not_found(self, mock_model):
        mock_model.get.side_effect = DoesNotExist()
        response = get({'path': {'todo_id': '1'}}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('NOT_FOUND', body_json['error'])
        self.assertEquals('TODO was not found', body_json['error_message'])
        self.assertEqual(response['statusCode'], 404)

    def test_successfully(self, mock_model):
        todo_item = {'todo_id': '1', 'text': 'hello'}
        mock_model.get.return_value = todo_item

        response = get({'path': {'todo_id': '1'}}, self.context_mock)
        mock_model.get.assert_called_once_with(hash_key='1')
        body_json = json.loads(response['body'])
        self.assertEquals('error' in body_json, False)
        self.assertEquals('error_message' in body_json, False)
        self.assertEquals(body_json, todo_item)
        self.assertEqual(response['statusCode'], 200)

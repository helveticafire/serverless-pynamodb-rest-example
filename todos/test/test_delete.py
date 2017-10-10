import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from pynamodb.exceptions import DoesNotExist, DeleteError

from todos.delete import handle
from todos.test.test_todo_model_integration import TestIntegrationBase


@patch('todos.delete.TodoModel')
@patch('os.environ', {})
class TestGetEnvVar(TestCase):
    def test_env_missing_vars(self, _):
        context_mock = MagicMock(function_name='delete', aws_request_id='123')
        response = handle({}, context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('ENV_VAR_NOT_SET', body_json['error'])
        self.assertEquals('\'DYNAMODB_TABLE\' is missing from environment variables', body_json['error_message'])
        self.assertEqual(response['statusCode'], 500)


@patch('todos.delete.TodoModel')
@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
class TestDelete(TestCase):
    def setUp(self):
        self.context_mock = MagicMock(function_name='delete', aws_request_id='123')
        super().setUp()

    def test_path_param_missing(self, _):
        response = handle({}, self.context_mock)
        self.assertIn('URL_PARAMETER_MISSING', response['body'])
        body_json = json.loads(response['body'])
        self.assertEquals('URL_PARAMETER_MISSING', body_json['error'])
        self.assertEquals('TODO id missing from url', body_json['error_message'])

        self.assertEqual(response['statusCode'], 400)

    def test_todo_not_found(self, mock_model):
        mock_model.get.side_effect = DoesNotExist()
        response = handle({'pathParameters': {'todo_id': '1'}}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('NOT_FOUND', body_json['error'])
        self.assertEquals('TODO was not found', body_json['error_message'])
        self.assertEqual(response['statusCode'], 404)

    def test_todo_cannot_delete(self, mock_model):
        found_todo = MagicMock()
        found_todo.delete.side_effect = DeleteError()
        mock_model.get.return_value = found_todo
        response = handle({'pathParameters': {'todo_id': '1'}}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('DELETE_FAILED', body_json['error'])
        self.assertEquals('Unable to delete the TODO', body_json['error_message'])
        self.assertEqual(response['statusCode'], 400)

    def test_delete_success(self, mock_model):
        found_todo = MagicMock()
        found_todo.checked = False
        found_todo.text = "blah"
        mock_model.get.return_value = found_todo
        response = handle({'pathParameters': {'todo_id': '1'}}, self.context_mock)
        self.assertEquals('body' in response, False)
        mock_model.get.assert_called_once_with(hash_key='1')
        found_todo.delete.assert_called_once()
        self.assertEqual(response['statusCode'], 204)


@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
class TestDeleteIntegration(TestIntegrationBase):
    def setUp(self, load_dbs=None):
        self.context_mock = MagicMock(function_name='delete', aws_request_id='123')
        super().setUp(load_dbs=[os.path.join(self.dir_path, 'fixtures/todo_db_0.json')])

    def test_delete(self):
        response = handle({'pathParameters': {'todo_id': 'd490d766-8b60-11e7-adba-e0accb8996e6'}}, self.context_mock)
        self.assertEqual(response['statusCode'], 204)

    def test_delete_get_failed(self):
        response = handle({'pathParameters': {'todo_id': 'd490d766-8b60-11e7-adba-e0accb8996e6a'}}, self.context_mock)
        self.assertEqual(response['statusCode'], 404)
        body_json = json.loads(response['body'])
        self.assertEquals('error' in body_json, True)
        self.assertEquals(body_json['error'], 'NOT_FOUND')
        self.assertEquals(body_json['error_message'], 'TODO was not found')

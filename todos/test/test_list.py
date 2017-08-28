import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from todos.list import todo_list
from todos.test.test_todo_model_integration import TestIntegrationBase


@patch('todos.list.TodoModel')
@patch('os.environ', {})
class TestListEnvVar(TestCase):
    def test_env_missing_vars(self, _):
        context_mock = MagicMock(function_name='list', aws_request_id='123')
        response = todo_list({}, context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('ENV_VAR_NOT_SET', body_json['error'])
        self.assertEquals('\'DYNAMODB_TABLE\' is missing from environment variables', body_json['error_message'])
        self.assertEqual(response['statusCode'], 500)


@patch('todos.list.TodoModel')
@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
class TestList(TestCase):
    def setUp(self):
        self.context_mock = MagicMock(function_name='list', aws_request_id='123')
        super(TestList, self).setUp()

    def test_list_success(self, mock_model):
        todo_item = {'todo_id': '1', 'text': 'hello'}
        mock_model.scan.return_value = [todo_item]
        response = todo_list({}, self.context_mock)
        mock_model.scan.assert_called_once()
        body_json = json.loads(response['body'])
        self.assertEquals('error' in body_json, False)
        self.assertEquals('error_message' in body_json, False)
        self.assertEquals('items' in body_json, True)
        self.assertEquals(body_json['items'][0], todo_item)
        self.assertEqual(response['statusCode'], 200)


@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
class TestListIntegration(TestIntegrationBase):
    def setUp(self, load_dbs=None):
        self.context_mock = MagicMock(function_name='list', aws_request_id='123')
        super().setUp(load_dbs=[os.path.join(self.dir_path, 'fixtures/todo_db_0.json')])

    def test_scan(self):
        response = todo_list({}, self.context_mock)
        self.assertEqual(response['statusCode'], 200)
        body_json = json.loads(response['body'])
        self.assertEquals('error' in body_json, False)
        self.assertEquals('error_message' in body_json, False)
        self.assertEquals('items' in body_json, True)
        self.assertEquals(len(body_json['items']), 1)
        self.assertListEqual(body_json['items'], [{'checked': False,
                                                   'created_at': '2017-08-27T21:49:25.310975+0000',
                                                   'text': 'text of d490d766-8b60-11e7-adba-e0accb8996e6',
                                                   'todo_id': 'd490d766-8b60-11e7-adba-e0accb8996e6',
                                                   'updated_at': '2017-08-27T21:49:25.779499+0000'}])

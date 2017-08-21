import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from todos.list import todo_list


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

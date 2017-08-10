from unittest import TestCase
from mock import mock
from todos.list import todo_list


@mock.patch('todos.list.TodoModel')
@mock.patch('os.environ', {})
class TestListEnvVar(TestCase):

    def test_env_missing_vars(self, _):
        context_mock = mock.MagicMock()
        context_mock.function_name = 'create'
        context_mock.aws_request_id = '123'
        response = todo_list({}, context_mock)
        self.assertIn('ENV_VAR_NOT_SET', response['body'])
        self.assertEqual(response['statusCode'], 500)

@mock.patch('todos.list.TodoModel')
@mock.patch('os.environ', {'DYNAMODB_TABLE': 'todo_table'})
class TestList(TestCase):

    def setUp(self):
        self.context_mock = mock.MagicMock()
        self.context_mock.function_name = 'create'
        self.context_mock.aws_request_id = '123'
        super(TestList, self).setUp()

    def test_list_success(self, mock_model):
        mock_model.scan.return_value = [{'todo_id': '1', 'text': 'hello'}]
        response = todo_list({}, self.context_mock)
        self.assertNotIn('NOT_FOUND', response['body'])
        self.assertIn('items', response['body'])
        self.assertIn('hello', response['body'])
        self.assertEqual(response['statusCode'], 200)

from unittest import TestCase
from mock import mock
from pynamodb.exceptions import DoesNotExist
from todos.get import get


@mock.patch('todos.get.TodoModel')
@mock.patch('os.environ', {})
class TestGetEnvVar(TestCase):

    def test_env_missing_vars(self, _):
        context_mock = mock.MagicMock()
        context_mock.function_name = 'create'
        context_mock.aws_request_id = '123'
        response = get({}, context_mock)
        self.assertIn('ENV_VAR_NOT_SET', response['body'])
        self.assertEqual(response['statusCode'], 500)

@mock.patch('todos.get.TodoModel')
@mock.patch('os.environ', {'DYNAMODB_TABLE': 'todo_table'})
class TestGet(TestCase):

    def setUp(self):
        self.context_mock = mock.MagicMock()
        self.context_mock.function_name = 'create'
        self.context_mock.aws_request_id = '123'
        super(TestGet, self).setUp()

    def test_path_param_missing(self, _):
        response = get({}, self.context_mock)
        self.assertIn('URL_PARAMETER_MISSING', response['body'])
        self.assertEqual(response['statusCode'], 422)

    def test_todo_not_found(self, mock_model):
        mock_model.get.side_effect = DoesNotExist()
        response = get({'path': {'todo_id': '1'}}, self.context_mock)
        self.assertIn('NOT_FOUND', response['body'])
        self.assertEqual(response['statusCode'], 404)

    def test_successfully(self, mock_model):
        response = get({'path': {'todo_id': '1'}}, self.context_mock)
        self.assertNotIn('NOT_FOUND', response['body'])
        self.assertEqual(response['statusCode'], 200)

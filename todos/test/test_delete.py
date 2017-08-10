

from unittest import TestCase
from mock import mock
from pynamodb.exceptions import DoesNotExist, DeleteError
from todos.delete import delete


@mock.patch('todos.delete.TodoModel')
@mock.patch('os.environ', {})
class TestGetEnvVar(TestCase):

    def test_env_missing_vars(self, _):
        context_mock = mock.MagicMock()
        context_mock.function_name = 'create'
        context_mock.aws_request_id = '123'
        response = delete({}, context_mock)
        self.assertIn('ENV_VAR_NOT_SET', response['body'])
        self.assertEqual(response['statusCode'], 500)

@mock.patch('todos.delete.TodoModel')
@mock.patch('os.environ', {'DYNAMODB_TABLE': 'todo_table'})
class TestDelete(TestCase):

    def setUp(self):
        self.context_mock = mock.MagicMock()
        self.context_mock.function_name = 'create'
        self.context_mock.aws_request_id = '123'
        super(TestDelete, self).setUp()

    def test_path_param_missing(self, _):
        response = delete({}, self.context_mock)
        self.assertIn('URL_PARAMETER_MISSING', response['body'])
        self.assertEqual(response['statusCode'], 422)

    def test_todo_not_found(self, mock_model):
        mock_model.get.side_effect = DoesNotExist()
        response = delete({'path': {'todo_id': '1'}}, self.context_mock)
        self.assertIn('NOT_FOUND', response['body'])
        self.assertEqual(response['statusCode'], 404)

    def test_todo_cannot_delete(self, mock_model):
        found_todo = mock.MagicMock()
        found_todo.delete.side_effect = DeleteError()
        mock_model.get.return_value = found_todo
        response = delete({'path': {'todo_id': '1'}}, self.context_mock)
        self.assertIn('DELETE_FAILED', response['body'])
        self.assertEqual(response['statusCode'], 400)

    def test_delete_success(self, mock_model):
        response = delete({'path': {'todo_id': '1'}}, self.context_mock)
        self.assertNotIn('body', response)
        self.assertEqual(response['statusCode'], 204)

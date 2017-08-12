from unittest import TestCase

from mock import mock
from pynamodb.exceptions import DoesNotExist

from todos.update import update


@mock.patch('todos.update.TodoModel')
@mock.patch('os.environ', {})
class TestUpdateEnvVar(TestCase):
    def test_env_missing_vars(self, _):
        context_mock = mock.MagicMock()
        context_mock.function_name = 'create'
        context_mock.aws_request_id = '123'
        response = update({}, context_mock)
        self.assertIn('ENV_VAR_NOT_SET', response['body'])
        self.assertEqual(response['statusCode'], 500)


@mock.patch('todos.update.TodoModel')
@mock.patch('os.environ', {'DYNAMODB_TABLE': 'todo_table'})
class TestUpdate(TestCase):
    def setUp(self):
        self.context_mock = mock.MagicMock()
        self.context_mock.function_name = 'create'
        self.context_mock.aws_request_id = '123'
        super(TestUpdate, self).setUp()

    def test_path_param_missing(self, _):
        response = update({}, self.context_mock)
        self.assertIn('URL_PARAMETER_MISSING', response['body'])
        self.assertEqual(response['statusCode'], 422)

    def test_bad_json(self, _):
        response = update({'body': '', 'path': {'todo_id': '1'}}, self.context_mock)
        self.assertIn('JSON_IRREGULAR', response['body'])
        self.assertEqual(response['statusCode'], 400)

    def test_todo_not_found(self, mock_model):
        mock_model.get.side_effect = DoesNotExist()
        response = update({'path': {'todo_id': '1'}}, self.context_mock)
        self.assertIn('NOT_FOUND', response['body'])
        self.assertEqual(response['statusCode'], 404)

    def test_text_missing(self, _):
        with mock.patch('todos.create.logging.error'):
            response = update({'path': {'todo_id': '1'},
                               'body': '{}'}, self.context_mock)
            self.assertIn('VALIDATION_FAILED', response['body'])
            self.assertEqual(response['statusCode'], 422)

    def test_successfully(self, _):
        response = update({'path': {'todo_id': '1'},
                           'body': '{"text": "blah", "checked": true}'}, self.context_mock)
        self.assertNotIn('NOT_FOUND', response['body'])
        self.assertEqual(response['statusCode'], 200)

    def test_no_change(self, mock_model):
        found_todo = mock.MagicMock()
        found_todo.checked = True
        found_todo.text = "blah"
        mock_model.get.return_value = found_todo
        with mock.patch('todos.create.logging.info'):
            response = update({'path': {'todo_id': '1'},
                               'body': '{"text": "blah", "checked": true}'}, self.context_mock)
            self.assertNotIn('NOT_FOUND', response['body'])
            self.assertEqual(response['statusCode'], 200)

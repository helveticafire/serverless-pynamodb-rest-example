import json
from unittest import TestCase

from mock import mock
from pynamodb.exceptions import DoesNotExist

from todos.update import update


@mock.patch('todos.update.TodoModel')
@mock.patch('os.environ', {})
class TestUpdateEnvVar(TestCase):
    def test_env_missing_vars(self, _):
        context_mock = mock.MagicMock(function_name='update', aws_request_id='123')
        response = update({}, context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('ENV_VAR_NOT_SET', body_json['error'])
        self.assertEquals('\'DYNAMODB_TABLE\' is missing from environment variables', body_json['error_message'])
        self.assertEqual(response['statusCode'], 500)


@mock.patch('todos.update.TodoModel')
@mock.patch('os.environ', {'DYNAMODB_TABLE': 'todo_table'})
class TestUpdate(TestCase):
    def setUp(self):
        self.context_mock = mock.MagicMock(function_name='update', aws_request_id='123')
        super(TestUpdate, self).setUp()

    def test_path_param_missing(self, _):
        response = update({}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('URL_PARAMETER_MISSING', body_json['error'])
        self.assertEquals('TODO id missing from url', body_json['error_message'])
        self.assertEqual(response['statusCode'], 422)

    def test_bad_json(self, _):
        response = update({'body': '', 'path': {'todo_id': '1'}}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('JSON_IRREGULAR', body_json['error'])
        self.assertEquals('No JSON object could be decoded', body_json['error_message'])
        self.assertEqual(response['statusCode'], 400)

    def test_todo_not_found(self, mock_model):
        mock_model.get.side_effect = DoesNotExist()
        response = update({'path': {'todo_id': '1'}}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('NOT_FOUND', body_json['error'])
        self.assertEquals('TODO was not found', body_json['error_message'])
        self.assertEqual(response['statusCode'], 404)

    def test_text_missing(self, _):
        with mock.patch('todos.create.logging.error'):
            response = update({'path': {'todo_id': '1'},
                               'body': '{}'}, self.context_mock)
            body_json = json.loads(response['body'])
            self.assertEquals('VALIDATION_FAILED', body_json['error'])
            self.assertEquals('Couldn\'t update the todo item.', body_json['error_message'])
            self.assertEqual(response['statusCode'], 422)

    def test_update_successful(self, mock_model):
        found_todo = mock.MagicMock()
        found_todo.checked = False
        found_todo.text = "blah"
        mock_model.get.return_value = found_todo
        response = update({'path': {'todo_id': '1'},
                           'body': '{"text": "blah", "checked": true}'}, self.context_mock)
        body_json = json.loads(response['body'])
        mock_model.get.assert_called_once_with(hash_key='1')
        found_todo.save.assert_called_once()
        # TODO: Test response is correct
        self.assertEquals('NOT_FOUND' in body_json, False)
        self.assertEqual(response['statusCode'], 200)

    def test_no_change(self, mock_model):
        found_todo = mock.MagicMock()
        found_todo.checked = True
        found_todo.text = "blah"
        mock_model.get.return_value = found_todo
        with mock.patch('todos.create.logging.info'):
            response = update({'path': {'todo_id': '1'},
                               'body': '{"text": "blah", "checked": true}'}, self.context_mock)
            mock_model.get.assert_called_once_with(hash_key='1')
            body_json = json.loads(response['body'])
            # TODO: Test response is correct
            self.assertEquals('NOT_FOUND' in body_json, False)
            self.assertEqual(response['statusCode'], 200)

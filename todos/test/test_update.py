import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from freezegun import freeze_time
from pynamodb.exceptions import DoesNotExist

from todos.test.test_todo_model_integration import TestIntegrationBase
from todos.update import handle


@patch('todos.update.TodoModel')
@patch('os.environ', {})
class TestUpdateEnvVar(TestCase):
    def test_env_missing_vars(self, _):
        context_mock = MagicMock(function_name='update', aws_request_id='123')
        response = handle({}, context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('ENV_VAR_NOT_SET', body_json['error_code'])
        self.assertEquals('\'DYNAMODB_TABLE\' is missing from environment variables', body_json['error_message'])
        self.assertEqual(response['statusCode'], 500)


@patch('todos.update.TodoModel')
@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
class TestUpdate(TestCase):
    def setUp(self):
        self.context_mock = MagicMock(function_name='update', aws_request_id='123')
        super().setUp()

    def test_path_param_missing(self, _):
        response = handle({}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('URL_PARAMETER_MISSING', body_json['error_code'])
        self.assertEquals('TODO id missing from url', body_json['error_message'])
        self.assertEqual(response['statusCode'], 400)

    def test_bad_json(self, _):
        response = handle({'body': '', 'pathParameters': {'todo_id': '1'}}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('JSON_IRREGULAR', body_json['error_code'])
        self.assertEquals('Expecting value: line 1 column 1 (char 0)', body_json['error_message'])
        self.assertEqual(response['statusCode'], 400)

    def test_todo_not_found(self, mock_model):
        mock_model.get.side_effect = DoesNotExist()
        response = handle({'pathParameters': {'todo_id': '1'}}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('NOT_FOUND', body_json['error_code'])
        self.assertEquals('TODO was not found', body_json['error_message'])
        self.assertEqual(response['statusCode'], 404)

    def test_text_missing(self, _):
        with patch('todos.create.logging.error'):
            response = handle({'pathParameters': {'todo_id': '1'},
                               'body': '{}'}, self.context_mock)
            body_json = json.loads(response['body'])
            self.assertEquals('VALIDATION_FAILED', body_json['error_code'])
            self.assertEquals('Could not update the todo item.', body_json['error_message'])
            self.assertEqual(response['statusCode'], 400)

    def test_update_successful(self, mock_model):
        found_todo = MagicMock()
        found_todo.checked = False
        found_todo.text = "todo 1"
        mock_model.get.return_value = found_todo
        response = handle({'pathParameters': {'todo_id': '1'},
                           'body': '{"text": "todo 1 update", "checked": true}'}, self.context_mock)
        body_json = json.loads(response['body'])
        mock_model.get.assert_called_once_with(hash_key='1')
        found_todo.save.assert_called_once()
        # TODO: Test response is correct
        self.assertEquals('NOT_FOUND' in body_json, False)
        self.assertEqual(response['statusCode'], 200)

    def test_no_change(self, mock_model):
        found_todo = MagicMock()
        found_todo.checked = True
        found_todo.text = "blah"
        mock_model.get.return_value = found_todo
        with patch('todos.create.logging.info'):
            response = handle({'pathParameters': {'todo_id': '1'},
                               'body': '{"text": "blah", "checked": true}'}, self.context_mock)
            mock_model.get.assert_called_once_with(hash_key='1')
            body_json = json.loads(response['body'])
            # TODO: Test response is correct
            self.assertEquals('NOT_FOUND' in body_json, False)
            self.assertEqual(response['statusCode'], 200)


@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
@freeze_time("2017-01-14 12:00:01")
class TestDeleteIntegration(TestIntegrationBase):
    def setUp(self, load_dbs=None):
        self.context_mock = MagicMock(function_name='delete', aws_request_id='123')
        super().setUp(load_dbs=[os.path.join(self.dir_path, 'fixtures/todo_db_0.json')])

    def test_update(self):
        response = handle({'pathParameters': {'todo_id': 'd490d766-8b60-11e7-adba-e0accb8996e6'},
                           'body': '{"text": "yayaya", "checked": true}'}, self.context_mock)
        self.assertEqual(response['statusCode'], 200)
        body_json = json.loads(response['body'])
        self.assertDictEqual(body_json, {'checked': True,
                                         'created_at': '2017-08-27T21:49:25.310975+0000',
                                         'text': 'yayaya',
                                         'todo_id': 'd490d766-8b60-11e7-adba-e0accb8996e6',
                                         'updated_at': '2017-01-14T12:00:01.000000+0000'})

    def test_update_get_failed(self):
        response = handle({'pathParameters': {'todo_id': 'd490d766-8b60-11e7-adba-e0accb8996e6a'},
                           'body': '{"text": "blah", "checked": true}'}, self.context_mock)
        self.assertEqual(response['statusCode'], 404)
        body_json = json.loads(response['body'])
        self.assertEquals('error_code' in body_json, True)
        self.assertEquals(body_json['error_code'], 'NOT_FOUND')
        self.assertEquals(body_json['error_message'], 'TODO was not found')

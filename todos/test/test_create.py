import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from freezegun import freeze_time

from todos.create import handle
from todos.test.test_todo_model_integration import TestIntegrationBase


@patch('todos.create.TodoModel')
class TestCreateEnvVar(TestCase):
    @patch('os.environ', {})
    def test_env_missing_all_vars(self, _):
        context_mock = MagicMock(function_name='create', aws_request_id='123')
        response = handle({}, context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('ENV_VAR_NOT_SET', body_json['error'])
        self.assertEquals('\'DYNAMODB_TABLE\' is missing from environment variables', body_json['error_message'])
        self.assertEqual(response['statusCode'], 500)


@patch('todos.create.TodoModel')
@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
class TestCreate(TestCase):
    def setUp(self):
        self.context_mock = MagicMock(function_name='create', aws_request_id='123')
        super(TestCreate, self).setUp()

    def test_bad_json(self, _):
        response = handle({'body': ''}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('JSON_IRREGULAR', body_json['error'])
        self.assertEquals('Expecting value: line 1 column 1 (char 0)', body_json['error_message'])
        self.assertEqual(response['statusCode'], 400)

    def test_text_missing_from_body(self, _):
        with patch('todos.create.logging.error'):
            response = handle({'body': '{}'}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEquals('BODY_PROPERTY_MISSING', body_json['error'])
        self.assertEquals('Couldn\'t create the todo item.', body_json['error_message'])
        self.assertEqual(response['statusCode'], 422)

    def test_text_value_empty(self, _):
        with patch('todos.create.logging.error'):
            response = handle({'body': '{"text": ""}'}, self.context_mock)
            body_json = json.loads(response['body'])
            self.assertEquals('VALIDATION_FAILED', body_json['error'])
            self.assertEquals('Couldn\'t create the todo item. As text was empty.', body_json['error_message'])
            self.assertEqual(response['statusCode'], 422)

    def test_create(self, mock_model):
        with patch('uuid.uuid1', return_value='3f248497-7fa5-11e7-a657-e0accb8996e6') as mock_id:
            created_todo = MagicMock(text='blah', todo_id=mock_id)
            mock_model.return_value = created_todo
            response = handle({'body': '{"text": "blah"}'}, self.context_mock)
            body_json = json.loads(response['body'])
            # TODO: figure out why this is not working. -
            created_todo.save.assert_called()
            # TODO: Test response is correct
            self.assertEquals('error' in body_json, False)
            self.assertEquals('error_message' in body_json, False)
            self.assertEqual(response['statusCode'], 201)


@patch('os.environ', {'DYNAMODB_TABLE': 'todo_table',
                      'DYNAMODB_REGION': 'eu-central-1'})
@patch('uuid.uuid1', return_value='3f248497-7fa5-11e7-a657-e0accb8996e6')
@freeze_time("2012-01-14 12:00:01")
class TestCreateIntegration(TestIntegrationBase):
    def setUp(self):
        self.context_mock = MagicMock(function_name='create', aws_request_id='123')
        super(TestCreateIntegration, self).setUp()

    def test_create(self, _):
        response = handle({'body': '{"text": "blah"}'}, self.context_mock)
        body_json = json.loads(response['body'])
        self.assertEqual(response['statusCode'], 201)
        self.assertEquals('error' in body_json, False)
        self.assertEquals('error_message' in body_json, False)

        self.assertEquals('todo_id' in body_json, True)
        self.assertEquals('text' in body_json, True)
        self.assertEquals('checked' in body_json, True)
        self.assertEquals('created_at' in body_json, True)
        self.assertEquals('updated_at' in body_json, True)
        self.assertDictEqual(body_json, {'checked': False,
                                         'created_at': '2012-01-14T12:00:01.000000+0000',
                                         'text': 'blah',
                                         'todo_id': '3f248497-7fa5-11e7-a657-e0accb8996e6',
                                         'updated_at': '2012-01-14T12:00:01.000000+0000'})

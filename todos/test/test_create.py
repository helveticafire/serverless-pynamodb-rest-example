from unittest import TestCase

import mock

from todos.create import create


@mock.patch('todos.create.TodoModel')
class TestCreateSuccess(TestCase):
    def test_create(self, _):
        with mock.patch('os.environ', {'DYNAMODB_TABLE': 'blah'}):
            mock_context = mock.MagicMock()
            mock_context.function_name = 'create'
            mock_context.aws_request_id = '123'
            response = create({'body': '{"text": "blah"}'}, mock_context)
            self.assertNotIn('ENV_VAR_NOT_SET', response['body'])
            self.assertEqual(response['statusCode'], 201)


@mock.patch('todos.create.TodoModel')
@mock.patch('os.environ', {})
class TestCreateEnvVar(TestCase):
    def test_env_missing_vars(self, _):
        context_mock = mock.MagicMock()
        context_mock.function_name = 'create'
        context_mock.aws_request_id = '123'
        response = create({}, context_mock)
        self.assertIn('ENV_VAR_NOT_SET', response['body'])
        self.assertEqual(response['statusCode'], 500)


@mock.patch('todos.create.TodoModel')
@mock.patch('os.environ', {'DYNAMODB_TABLE': 'todo_table'})
class TestCreate(TestCase):
    def setUp(self):
        self.context_mock = mock.MagicMock()
        self.context_mock.function_name = 'create'
        self.context_mock.aws_request_id = '123'
        super(TestCreate, self).setUp()

    def test_bad_json(self, _):
        response = create({'body': ''}, self.context_mock)
        self.assertIn('JSON_IRREGULAR', response['body'])
        self.assertEqual(response['statusCode'], 400)

    def test_text_missing_from_body(self, _):
        with mock.patch('todos.create.logging.error'):
            response = create({'body': '{}'}, self.context_mock)
            self.assertIn('BODY_PROPERTY_MISSING', response['body'])
            self.assertEqual(response['statusCode'], 422)

    def test_text_value_empty(self, _):
        with mock.patch('todos.create.logging.error'):
            response = create({'body': '{"text": ""}'}, self.context_mock)
            self.assertIn('VALIDATION_FAILED', response['body'])
            self.assertEqual(response['statusCode'], 422)

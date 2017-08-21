from unittest import TestCase
import datetime
from unittest.mock import patch, MagicMock

from freezegun import freeze_time

from todos.todo_model import TodoModel


class TestTodoModel(TestCase):
    @patch('todos.todo_model.Model.save')
    @freeze_time("2012-01-14 12:00:01")
    def test_save(self, _):
        t_model = TodoModel()
        t_model.save()
        self.assertEquals(t_model.updated_at, datetime.datetime(2012, 1, 14, 12, 0, 1))

    def test_setup_model(self):
        mock_model = MagicMock()
        mock_model.Meta.host = 'http://localhost:8000'
        table = 'table'
        region = 'region'
        TodoModel.setup_model(mock_model, region, table, False)
        self.assertEquals(mock_model.Meta.table_name, table)
        self.assertEquals(mock_model.Meta.region, region)
        self.assertEquals(mock_model.Meta.host, 'http://localhost:8000')

        table = 'table1'
        region = 'region1'
        TodoModel.setup_model(mock_model, region, table, True)
        self.assertEquals(mock_model.Meta.table_name, table)
        self.assertEquals(mock_model.Meta.region, region)
        self.assertEquals(mock_model.Meta.host, 'https://dynamodb.{0}.amazonaws.com'.format(region))

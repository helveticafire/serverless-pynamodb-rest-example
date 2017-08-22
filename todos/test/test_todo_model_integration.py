from unittest import TestCase

from todos.todo_model import TodoModel


class TestTodoModelIntegration(TestCase):
    def setUp(self):
        TodoModel.setup_model(TodoModel, 'region', 'todo')
        if not TodoModel.exists():
            TodoModel.create_table(wait=True)
        super(TestTodoModelIntegration, self).setUp()

    def test_create(self):
        todo_text = 'text'
        todo_id = '1'
        t1 = TodoModel(todo_id=todo_id,
                       text=todo_text)
        t1.save()
        self.assertEquals(t1.text, todo_text)
        self.assertEquals(t1.checked, False)
        t2 = TodoModel.get(hash_key=todo_id)
        self.assertEquals(t2.text, todo_text)
        r = [result for result in TodoModel.scan()]
        self.assertEquals(len(r), 1)
        self.assertEquals(r[0].text, todo_text)
        self.assertEquals(r[0].todo_id, todo_id)
        t2.delete()

    def tearDown(self):
        if TodoModel.exists():
            TodoModel.delete_table()
        super(TestTodoModelIntegration, self).tearDown()

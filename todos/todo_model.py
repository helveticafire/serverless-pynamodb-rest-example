from datetime import datetime

from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute
from pynamodb.models import Model


class TodoModel(Model):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        region = 'localhost'
        host = 'http://localhost:8000'

    todo_id = UnicodeAttribute(hash_key=True, null=False)
    text = UnicodeAttribute(null=False)
    checked = BooleanAttribute(null=False, default=False)
    created_at = UTCDateTimeAttribute(null=False)
    updated_at = UTCDateTimeAttribute(null=False)

    def save(self, conditional_operator=None, **expected_values):
        self.updated_at = datetime.now()
        super(TodoModel, self).save()

    def __iter__(self):
        for name, attr in self._get_attributes().items():
            yield name, attr.serialize(getattr(self, name))

    @staticmethod
    def setup_model(model, region, table_name, is_remote=False):
        model.Meta.table_name = table_name
        model.Meta.region = region
        if is_remote:
            model.Meta.host = 'https://dynamodb.{0}.amazonaws.com'.format(region)

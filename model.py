import config
from peewee import Model, BigIntegerField, CharField, IntegerField, DateTimeField, BooleanField, PostgresqlDatabase

database = PostgresqlDatabase(
    config.database['name'],
    user=config.database['user'],
    password=config.database['password'],
    host=config.database['host']
)


class BaseModel(Model):
    class Meta:
        database = database


class Star(BaseModel):
    message_id = BigIntegerField(primary_key=True)
    channel_id = BigIntegerField()  # Needed to fetch the original message
    star_id = BigIntegerField()  # The ID of the star message
    username = CharField()
    avatar_url = CharField()
    channel = CharField()
    jump_link = CharField()
    content = CharField(null=True, max_length=2000)  # Same as discord max length
    attachment_url = CharField(null=True)
    votes = IntegerField()
    timestamp = DateTimeField()

    class Meta:
        table_name = 'stars'

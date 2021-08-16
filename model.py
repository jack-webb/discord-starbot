import os

from peewee import Model, BigIntegerField, CharField, IntegerField, DateTimeField, SqliteDatabase

database = SqliteDatabase(os.path.join("stars.db"))


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

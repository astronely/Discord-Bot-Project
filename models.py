from peewee import *

db = SqliteDatabase('db/DiscordBot.db')

class BaseModel(Model):
    class Meta:
        database = db

class Chats(BaseModel):
    chat = CharField()
    id = IntegerField()

    class Meta:
        order_by = 'chat'
        db_table = 'chats'

class Logs(BaseModel):
    server = CharField()
    chat = CharField()
    id = IntegerField()

    class Meta:
        order_by = 'server'
        db_table = 'logs'

class Words(BaseModel):
    id = PrimaryKeyField(unique=True)
    name = CharField()
    level = IntegerField()

    class Meta:
        order_by = 'level'
        db_table = 'words'

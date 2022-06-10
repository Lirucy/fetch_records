from peewee import *
import datetime

from db import DATABASE

class Transaction(Model):
    payer = CharField()
    points = IntegerField(default=0)
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE
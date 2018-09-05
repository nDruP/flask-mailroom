import os

from functools import partial
from peewee import Model, CharField, ForeignKeyField, DecimalField
from playhouse.db_url import connect

db = connect(os.environ.get('DATABASE_URL', 'sqlite:///my_database.db'))
MoneyField = partial(DecimalField, decimal_places=2)


class Donor(Model):
    name = CharField(max_length=255, unique=True)

    class Meta:
        database = db


class Donation(Model):
    value = MoneyField()
    donor = ForeignKeyField(Donor, backref='donations')

    class Meta:
        database = db

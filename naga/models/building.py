import mongoengine as me
import hashlib
import datetime

class Building(me.Document):
    meta = {'collection': 'buildings'}

    team = me.StringField(max_length=7,required=True)
    name = me.StringField(max_length=50,required=True)
    hp = me.IntField(required=True)
    armor = me.IntField(required=True)
    position_x = me.IntField(required=True)
    position_y = me.IntField(required=True)

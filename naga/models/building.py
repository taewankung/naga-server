import mongoengine as me
import hashlib
import datetime

class Building(me.Document):
    meta = {'collection': 'buildings'}

    team = me.StringField(max_length=7,required=True)
    name = me.StringField(max_length=50,required=True)
    hp = me.IntField(required=True)
    armor = me.IntField(required=True)
    mana = me.IntField(required=True)
    hp_regen = me.FloatField(required=True)
    mana_regen = me.FloatField(required=True)
    damage = me.IntField(required=True)
    armor = me.IntField(required=True)
    damage_speed = me.FloatField(required=True)
    magic_resis = me.IntField(required=True)
    damage_range = me.FloatField(required=True)
    cost = me.IntField(required=True)
    position_x = me.IntField(required=True)
    position_y = me.IntField(required=True)

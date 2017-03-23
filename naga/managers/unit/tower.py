from .building import Building
from .sensor.enemy_sensor import EnemySensor
import time

class Tower(Building):
    def __init__(self,data_tower):
        super().__init__(data_tower)
        self.current_speed_dmg = time.time()
        self.damage_speed = self.data_unit.damage_speed
        self.enemy_list = []
        self.near_enemy_list = []
        self.num_current_enemy = len(self.near_enemy_list)
        self.enemy_sensor = EnemySensor(self,self.enemy_list)
        self.exp = 10
        self.bounty = self.data_unit.cost

    def update_enemy(self):
        self.enemy_sensor.unit_list = self.enemy_list
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan(in_range=100)
        self.num_current_enemy = len(self.near_enemy_list)

    def attack(self):
        #print('{0}: attack'.format(self.name))
        if len(self.near_enemy_list) != 0:
            if time.time()-self.current_speed_dmg >= self.damage_speed:
                self.near_enemy_list[0].current_hp = self.near_enemy_list[0].current_hp - self.damage
                self.current_speed_dmg = time.time()

    def to_data_dict(self):
        result = dict(id=self.id,
                name=self.name,
                max_hp=self.max_hp,
                current_hp=self.current_hp,
                hp_regen=self.hp_regen,
                max_mana=self.max_mana,
                current_mana=self.current_mana,
                mana_regen=self.mana_regen,
                damage=self.damage,
                armor=self.armor,
        #        take_damaged=self.take_damaged,
        #        buff_status=self.buff_status,
                pos_x=self.pos_x,
                pos_y=self.pos_y,
        #        range=self.range,
        #        id_controller=self.id_controller,
                alive=self.alive,)
        return result

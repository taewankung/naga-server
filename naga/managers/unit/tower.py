from .building import Building
from .sensor.enemy_sensor import EnemySensor

class Tower(Building):
    def __init__(self,data_tower):
        super().__init__(data_tower)
        self.current_speed_dmg = 0.0000000000000
        self.damage_speed = self.data_unit.damage_speed
        self.enemy_list = []
        self.near_enemy_list = []
        self.num_current_enemy = len(self.near_enemy_list)
        self.enemy_sensor = EnemySensor(self,self.enemy_list)
        self.exp = 10
        self.bounty = self.data_unit.cost

    def update_enemy(self):
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan(in_range=100)
        self.num_current_enemy = len(self.near_enemy_list)

    def attack(self):
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan()
        self.num_current_enemy = len(self.near_enemy_list)
        #print('{0}: attack'.format(self.name))
        if self.current_speed_dmg >= self.damage_speed:
            if len(self.near_enemy_list) != 0:
                self.near_enemy_list[0].current_hp = self.near_enemy_list[0].current_hp - self.damage
            self.current_speed_dmg = 0
        else:
            self.current_speed_dmg = self.current_speed_dmg + 0.001;

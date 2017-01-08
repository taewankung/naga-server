import math
from .unit import Unit
from .sensor.enemy_sensor import EnemySensor

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

class Creep(Unit):
    def __init__(self,data_unit,unit_range = 10):
        super().__init__(data_unit,
                         True,
                         [""],
                         data_unit.position_x,
                         data_unit.position_y,
                         unit_range
                         )
        self.move_speed = data_unit.move_speed
        self.sensor ={}
        self.can_move = False
        self.damage_speed = data_unit.damage_speed
        self.current_speed_dmg = 0
        self.enemy_list = []
        self.near_enemy_list = []
        self.num_current_enemy = len(self.near_enemy_list)
        self.enemy_sensor = EnemySensor(self,self.enemy_list)
        self.exp = 20
        self.bounty = 45
        self.state = 'walk'
        #  self.path = {'mid':{
                           #  },
                     #  'top':{},
                     #  'buttom':{}
                     #  }

    def change_controller(self,id_controller):
        self.id_controller = id_controller

    def run_behavior(self,lane='mid_team1'):
        if self.alive:
            if lane == 'mid_team1':
                if self.state =='walk':
                    self.move(1000,1000)
                elif self.state == 'found_enemy':
                    self.attack()

            if lane == 'mid_team2':
                if self.state =='walk':
                    self.move(0,0)
                elif self.state == 'found_enemy':
                    self.attack()

    def stop(self):
        self.state = 'stop'

    def move(self,pos_x,pos_y):
        pi = 3.14159265359
        m = (pos_y-self.pos_y)/(pos_x-self.pos_x)
        rad = math.atan(m)
        if pos_x < self.pos_x and pos_y < self.pos_y:
            rad = rad + pi
        elif pos_x < self.pos_x and pos_y > self.pos_y:
            rad = rad + pi
        forge_x = self.move_speed * math.cos(rad)*0.001
        forge_y = self.move_speed * math.sin(rad)*0.001
        if not isclose(pos_x,self.pos_x,1e-01) and self.pos_x < 1000 and self.pos_x > -1:
            self.pos_x += forge_x
        if not isclose(self.pos_y,pos_y,1e-01) and self.pos_y < 1000 and self.pos_y >= -1:
            self.pos_y += forge_y
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan()
        self.num_current_enemy = len(self.near_enemy_list)
        if num_old_enemy != self.num_current_enemy:
            self.state = 'found_enemy'

    def attack(self):
        #  num_old_enemy = self.num_current_enemy
        #  self.near_enemy_list = self.enemy_sensor.scan()
        #  self.num_current_enemy = len(self.near_enemy_list)
        if self.near_enemy_list !=[]:
           # print(self.near_enemy_list)
            enemy = self.near_enemy_list[0]
            if self.current_speed_dmg >= self.damage_speed:
                self.move(enemy.pos_x,enemy.pos_y)
                enemy.current_hp = enemy.current_hp - self.damage
                self.current_speed_dmg = 0
            else:
                self.current_speed_dmg = self.current_speed_dmg + 0.001
        else:
            self.state = 'walk'

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
                take_damaged=self.take_damaged,
                buff_status=self.buff_status,
                pos_x=self.pos_x,
                pos_y=self.pos_y,
                range=self.range,
                id_controller=self.id_controller,
                alive=self.alive,
                move_speed=self.move_speed)
        return result

import math
from .unit import Unit
from .sensor.enemy_sensor import EnemySensor


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


    def change_controller(self,id_controller):
        self.id_controller = id_controller

    def move(self,pos_x,pos_y):
        #  distance = math.sqrt(math.pow((self.pos_y-self.pos_y),2)+
                             #  math.pow((self.pos_x-pos_x),2)
                            #  )

        rad = (pos_y-self.pos_y)/(pos_x-self.pos_x)
        if( pos_x - self.pos_x < 0 or pos_y - self.pos_y<0):
            rad =-1*rad
        degree = math.atan(rad)
        force_x = self.move_speed * math.cos(degree)
        force_y = self.move_speed * math.sin(degree)
        force_x = force_x *0.001
        force_y = force_y *0.001
        if self.pos_x-pos_x > 0.1 or self.pos_x - pos_x < -0.1:
            self.pos_x += force_x
        if self.pos_y-pos_y > 0.1 or self.pos_y - pos_y < -0.1:
            self.pos_y += force_y
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan()
        self.num_current_enemy = len(self.near_enemy_list)

    def attack(self):
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan()
        self.num_current_enemy = len(self.near_enemy_list)
        for enemy in self.near_enemy_list:
            if enemy.name == target:
                if self.current_speed_dmg >= self.damage_speed:
                    enemy.current_hp = enemy.current_hp - self.damage
                    self.current_speed_dmg = 0
                else:
                    self.current_speed_dmg = self.current_speed_dmg + 0.001

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

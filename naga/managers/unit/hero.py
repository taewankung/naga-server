#import sys
#import os

#PACKAGE_PARENT = '..'
#SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
#sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from .unit import Unit
from .sensor.enemy_sensor import EnemySensor
import math

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

class Hero(Unit):
    def __init__(self,
                data_unit,
                position_x = 50,
                position_y = 50,
                unit_range = 50, #self.range = unit_range
                id_controller = 'system'
                ):
        super().__init__(
                         data_unit,
                         True,
                         [""],
                         position_x,
                         position_y,
                         unit_range,
                         id_controller
                         )
        self.str = self.data_unit.strength
        self.agi = self.data_unit.agility
        self.damage_critical = self.data_unit.damage_critical
        self.magic = self.data_unit.magic
        self.magic_resis = self.data_unit.magic_resis
        self.damage_speed = self.data_unit.damage_speed
        self.current_speed_dmg = 0
        self.move_speed = self.data_unit.move_speed
        self.skills = self.data_unit.skills
        self.critical_chance = self.data_unit.damage_critical
        self.level = 1
        self.kill = 0
        self.death = 0
        self.assist = 0
        self.lasthit = 0
        self.current_exp = 0
        self.damage_reduce = 0
        self.move_status = True
        self.skill_point = 1
        self.gold = 0
        self.act_status = dict(action="",
                               found_event=""
                              )
        #  self.target = None
        self.time_to_born = 0
        self.enemy_list = []
        self.near_enemy_list = []
        self.num_current_enemy = len(self.near_enemy_list)
        self.enemy_sensor = EnemySensor(self,self.enemy_list)
        self.current_exp = 0
        self.exp = 100
        self.exp_up = [0,200,250,300,450,500,
                       550,600,650,700,800,
                       900,1000,1100,1150,
                       1300,1450,1600,1750,
                       1900,2050,2200,2350,
                       2500,2650,2800,2950
                      ]

    def level_up(self):
        if self.level <=25:
            self.level = self.level + 1
            self.skill_point+=1


    def die(self):
        self.alive = False
        if self.time_to_born <=0 and not self.alive:
            self.act_status["found_event"]="died"
            self.time_to_born = self.level*15;

    def countdown_to_born(self):
        if self.time_to_born > 0:
            self.time_to_born = self.time_to_born - 0.01
        if self.time_to_born <=0:
            print('Reborn')
            self.reborn()

    def reborn(self):
        if not self.alive:
            self.alive = True
            self.act_status["found_event"]="reborn"
            self.current_hp = self.max_hp

    def get_status(self):
        status = {
                "hp": self.current_hp,
                "mana": self.current_mana,
                "str": self.str,
                "agi": self.agi,
                "damage": self.damage_critical,
                "magic": self.magic,
                "magic_resis": self.magic_resis,
                "damage_speed": self.damage_speed,
                "move_speed": self.move_speed,
                "skills": self.skills,
                "level": self.level,
                "kill": self.kill,
                "death": self.death,
                "assist": self.assist,
                "lasthit": self.lasthit,
                "current_exp":self.current_exp
                 }
        return status

    def attack(self,target):
        compleate = False
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan()
        self.num_current_enemy = len(self.near_enemy_list)
        for enemy in self.near_enemy_list:
            if enemy.name == target:
                if self.current_speed_dmg >= self.damage_speed:
                    enemy.current_hp = enemy.current_hp - self.damage
                    if enemy.current_hp <=0:
                        self.current_exp += enemy.exp
                        self.gold += enemy.bounty
                        if self.current_exp >= self.exp_up[self.level]:
                            self.level_up()
                    self.current_speed_dmg = 0
                else:
                    self.current_speed_dmg = self.current_speed_dmg + 0.001;
                if enemy.current_hp > 0:
                    compleate = False
                else:
                    compleate = True
        return compleate

    def move(self,pos_x,pos_y):
        finish_x = False
        finish_y = False
        complete = False
        pi = 3.14159265359
        if self.move_status:
            m = (pos_y-self.pos_y)/(pos_x-self.pos_x)
            rad = math.atan(m)
#            print(rad)
            if pos_x < self.pos_x and pos_y < self.pos_y:
                rad = rad + pi
            elif pos_x < self.pos_x and pos_y > self.pos_y:
                rad = rad + pi

            forge_x = self.move_speed * math.cos(rad)*0.001
            forge_y = self.move_speed * math.sin(rad)*0.001

        if not isclose(pos_x,self.pos_x,1e-01) and self.pos_x < 1000 and self.pos_x > -1:
            self.pos_x += forge_x
        else:
            finish_x = True
        if not isclose(self.pos_y,pos_y,1e-01) and self.pos_y < 1000 and self.pos_y >= -1:
            self.pos_y += forge_y
        else:
            finish_y = True
        if finish_y and finish_x:
            complete = True
        #print('finish_y:'+str(finish_y)+' finish_x'+str(finish_x))
#/////////////check enemy///////////////////
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan()
        self.num_current_enemy = len(self.near_enemy_list)
        if num_old_enemy < self.num_current_enemy:
            self.act_status["found_event"]="found_enemy"
        elif self.num_current_enemy ==0:
            self.act_status["found_event"]=""
        return complete
        #  if finish_x and finish_y:
            #  break

    def upgrade_skill(self,skill_number):
        print('upgrade skill:{}'.format(self.data_unit['skills'][skill_number]))

    def use_skill(self,skill_number):
        print('using skill:{}'.format(self.data_unit['skills'][skill_number]))

    def sell_item(self,item):
        print('sell_item')

    def buy_item(self,item):
        print('buy_item')

    def to_data_dict(self):
        result = dict(take_damaged=self.take_damaged,
                buff_status=self.buff_status,
                id_controller=self.id_controller,
                id=self.id,
                name=self.name,
                max_hp=self.max_hp,
                current_hp=self.current_hp,
                hp_regen=self.hp_regen,
                max_mana=self.max_mana,
                current_mana=self.current_mana,
                mana_regen=self.mana_regen,
                damage=self.damage,
                armor=self.armor,
                alive=self.alive,
                pos_x=self.pos_x,
                pos_y=self.pos_y,
                range=self.range,
                str=self.str,
                agi=self.agi,
                damage_critical=self.damage_critical,
                magic=self.magic,
                magic_resis=self.magic_resis,
                damage_speed=self.damage_speed,
                move_speed=self.move_speed,
                skills=self.skills,
                kill=self.skills,
                death=self.death,
                assist=self.assist,
                lasthit=self.lasthit,
                current_exp=self.current_exp,
                move_status=self.move_status,
                act_status=self.act_status,
                near_enemy_list=[enemy.to_data_dict() for enemy in self.near_enemy_list],
                time_to_born=self.time_to_born,
                gold = self.gold)
        return result

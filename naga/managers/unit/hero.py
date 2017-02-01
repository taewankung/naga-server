#import sys
#import os

#PACKAGE_PARENT = '..'
#SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
#sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from .unit import Unit
from .sensor.enemy_sensor import EnemySensor
from .sensor.team_sensor import TeamSensor
import math
from .tower import Tower
import time

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
        self.gold = 600
        self.bounty = 300
        self.act_status = dict(action="",
                               found_event=""
                              )
        self.item_list = []
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
        self.max_exp = self.exp_up[self.level]
#///////////////// skill attibute/////////////////////////
        self.skill_level=[0,0,0,0]
        self.current_cooldown=[0,0,0,0]
        self.skills = self.data_unit.skills
#///////////////// team attibute/////////////////////////
        self.team_list =[]
        self.near_team_list =[]
        self.num_current_team = len(self.near_team_list)
        self.team_sensor = TeamSensor(self,self.team_list)
        self.log=[]

    def level_up(self):
        if self.level <=25:
            self.level = self.level + 1
            self.skill_point +=1
            self.max_exp = self.exp_up[self.level]
            self.act_status["found_event"]="level_up"

    def use_skill(self,skill_number,target=''):
        code = 0
        used = False
        if self.skill_level[skill_number] != 0:
            skill_level = self.skill_level[skill_number]
            skill = self.skills[skill_number]
            #print(skill['name'])
            if skill['skill_type'] != 'buff_passive':
                if skill['skill_type'] == 'attack' and self.current_cooldown[skill_number]<=0 and self.current_mana >= skill['used_mana'][skill_level]:
                    for enemy in self.near_enemy_list:
                        if enemy.name == target:
                            enemy.current_hp = enemy.current_hp - skill['damage'][skill_level]
                            enemy.current_hp = enemy.current_hp - skill['magic'][skill_level]
                            self.current_cooldown[skill_number]= skill['cooldown'][skill_level]
                            self.current_mana -= skill['used_mana'][skill_level]
                            code = self.check_enemy_die(enemy)
                            used = True
                elif skill['skill_type'] == 'support':
                    code = 2
                    used = True
            #  if code == 0:
                #  if self.act_status["found_event"] !="can_not_use_skill":
                    #  self.act_status["found_event"]="can_not_use_skill"
            if code == 1:
                if self.act_status["found_event"] !="battle":
                    self.act_status["found_event"]="battle"
            elif code == 2:
                self.act_status["found_event"]="suport team"
            elif code == 3:
                self.act_status["found_event"]=""
            pass
        return used
            #print('do not upgraded skill')
#        print('using skill:{0}'.format(skill['skill_type']))


    def upgrade_skill(self,skill_num):
        if self.skill_point >0:
            self.skill_point -=1
            self.skill_level[skill_num] =+1
#            print('{0}: {1}'.format(self.name,self.skill_point))
            skill = self.skills[skill_num]
            level = self.skill_level[skill_num] =+1
            if skill['skill_type'] == 'buff_passive':
                if self.current_hp == self.max_hp:
                    self.max_hp += skill['buffs_hp'][level-1]
                    self.current_hp = self.max_hp
                if self.current_mana == self.max_mana:
#                    print('max_mana before: {0}'.format(self.max_mana))
                    self.max_mana += skill['buffs_mana'][level-1]
                    self.current_mana = self.max_mana
                elif self.current_mana < self.max_mana:
                    if self.current_mana+ 0.1*self.max_mana <= self.max_mana:
                        self.current_mana += 0.1*self.max_mana
                    else:
                        self.current_mana = self.max_mana
                self.damage_speed += skill['attack_speed'][level-1]
                self.armor += skill['buffs_armor'][level-1]
                self.damage += skill['buffs_damage'][level-1]
#                print('{0}: {1}'.format(self.name,self.max_mana))

    def buy_item(self,item_dict):
        buy = False
        if len(self.item_list) < 6 and self.gold >= item_dict['price']:
            print('buy_item')
#            print(dict(item_dict.to_mongo()))
            buy = True
            self.item_list.append(item_dict)
            self.gold -= item_dict['price']
            self.max_hp += item_dict['max_hp']
            self.max_mana += item_dict['max_mana']
            self.damage += item_dict['damage']
            self.move_speed += item_dict['move_speed']
        if not buy:
            self.act_status['found_event']='can not buy item'
            self.act_status['action'] ='can not buy item'
        else:
            print('success')
            print(buy)
        return buy

    def use_item(self,item_dict):
        use = False
        if item_dict in self.item_list:
            use = True
            if item_dict['type']==1:
                print('??')
                self.current_hp += item_dict['current_hp']
                self.current_mana += item_dict['current_mana']
                self.item_list.remove(item_dict)
        if not use:
            self.act_status['found_event']='can not use item'
            self.act_status['action'] ='can not use item'
        else:
            print('success')
        return use

    def die(self):
        self.alive = False
        if self.time_to_born <=0 and not self.alive:
            self.act_status["found_event"]="died"
            self.death = self.death+1
            self.time_to_born = self.level*5;
            self.current_cooldown = [0,0,0,0]
            self.current_mana = self.max_mana

#//////////////update near team////////////////////
    def scan_team_unit(self):
        num_old_team = self.num_current_team
        self.near_team_list = self.team_sensor.scan(in_range=50)
        self.num_current_enemy = len(self.near_enemy_list)
        return num_old_team

#/////////////update enemy ///////////////////
    def scan_enemy_unit(self):
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan()
        self.num_current_enemy = len(self.near_enemy_list)
        if num_old_enemy < self.num_current_enemy:
            self.act_status["found_event"]="found_enemy"
#            print('{0}:{1}'.format(self.name,[e.name for e in self.enemy_list]))
        elif self.num_current_enemy ==0:
            self.act_status["found_event"]=""
        return num_old_enemy
        #  if complete:
            #  print('{0}:{1}'.format(self.pos_x,self.pos_y))

    def countdown_to_born(self,time=0.001):
#        print(self.time_to_born)
        if self.time_to_born > 0:
            self.time_to_born = self.time_to_born - time
        if self.time_to_born <= 0 :
            print('Reborn')
            self.reborn()

    def count_cooldown(self,time=0.001):
        for cd in range(0,3):
            if self.current_cooldown[cd] > 0:
#                print(self.current_cooldown)
                self.current_cooldown[cd] = self.current_cooldown[cd] - time

    def reborn(self):
        if not self.alive:
            self.alive = True
            self.act_status["found_event"]="reborn"
            self.current_hp = self.max_hp

    def attack(self,target):
        compleate = False
        num_old_enemy = self.num_current_enemy
        self.near_enemy_list = self.enemy_sensor.scan()
        self.num_current_enemy = len(self.near_enemy_list)
        for enemy in self.near_enemy_list:
            if enemy.name == target:
                if time.time() - self.current_speed_dmg >= self.damage_speed:
                    enemy.current_hp = enemy.current_hp - self.damage
                    print('{0}:{1} {2}'.format(enemy.name,enemy.current_hp,self.damage))
                    if type(enemy) is Hero:
                        self.kill = self.kill+1
                        for team_unit in self.near_team_list:
                            if type(team_unit) is Hero:
                                team_unit.assist = team_unit.assist+1
                    elif type(enemy) is Creep:
                        self.lasthit =self.lasthit+1
                    self.check_enemy_die(enemy)
                    self.current_speed_dmg = time.time()
                if enemy.current_hp > 0:
                    compleate = False
                else:
                    compleate = True
        if not compleate:
                self.act_status["found_event"]="battle"
        else:
            self.act_status["found_event"]=""
        return compleate

    def check_enemy_die(self,enemy):
        if enemy.current_hp <=0:
            self.current_exp += enemy.exp
            self.gold += enemy.bounty
            if self.current_exp >= self.max_exp:
                self.current_exp = self.current_exp - self.max_exp
                self.level_up()
                return 3
            return 1

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

        if not isclose(pos_x,self.pos_x,1e-2) and self.pos_x < 1000 and self.pos_x > -1:
            self.pos_x += forge_x
        else:
            finish_x = True
        if not isclose(self.pos_y,pos_y,1e-2) and self.pos_y < 1000 and self.pos_y >= -1:
            self.pos_y += forge_y
        else:
            finish_y = True
        if finish_y and finish_x:
            complete = True
        self.scan_enemy_unit()
        return complete
        #  if finish_x and finish_y:
            #  break

    def sell_item(self,item):
        print('sell_item')

    #  def buy_item(self,item):
        #  print('buy_item')

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
                skill_level=self.skill_level,
                skill_point= self.skill_point,
                skill_cooldown = [cd for cd in self.current_cooldown],
                kill=self.kill,
                death=self.death,
                assist=self.assist,
                lasthit=self.lasthit,
                current_exp=self.current_exp,
                max_exp = self.max_exp,
                move_status=self.move_status,
                act_status=self.act_status,
                near_enemy_list=[enemy.name for enemy in self.near_enemy_list],
                near_team_list =[aliance.name for aliance in self.near_team_list],
                time_to_born=self.time_to_born,
                item=[item for item in self.item_list],
                level= self.level,
                gold = self.gold)
        return result

from .unit.hero import Hero
from .unit.tower import Tower
from .unit.building import Building
from .unit.creep import Creep
from naga import models
from naga.models.building import Building as building_a
from .scoreboard import ScoreBoard
from . import games
import json


class BattleArena:
    def __init__(self, players, size_x=1000, size_y=1000):
        self.players = players
        self.heros ={}
        self.hero_team1 = {}
        self.hero_team2 = {}
        self.tower_team1 ={}
        self.tower_team2 = {}
        self.creep_team1 = {}
        self.creep_team2 = {}
        self.base_team1 = None
        self.base_team2 = None
        self.nature_creep ={}
        self.scoreboard = ScoreBoard(self.hero_team1,self.hero_team2)

#////////Localtion in game////////////////
        self.game_location = {"spawn_creep_team1":(150,150),
                               "spawn_creep_team2":(850,850)
                              }

#//////Mehod///////////////////////////
    def to_data_dict(self):
        battle_arena_data = dict(#players = self.players,
                                 #heros = self.heros,
                                 hero_team1 = self.hero_team1,
                                 hero_team2 = self.hero_team2,
                                 tower_team1 = self.tower_team1,
                                 tower_team2 = self.tower_team2,
                                 creep_team1 = self.creep_team1,
                                 creep_team2 = self.creep_team2,
                                 base_team1 = self.base_team1,
                                 base_team2 = self.base_team2
                                )
        return battle_arena_data

    def schedule(self):
        pass

    def create_creep(self,target='mid'):
        c = models.Creep.objects(name = "Creep").first()
        c_data = games.GameUnit(**dict(c.to_mongo()))

        if target == 'mid':
            for i in range(1):
                creep = Creep(c_data)
                creep.pos_x = self.game_location['spawn_creep_team1'][0]
                creep.pos_y = self.game_location['spawn_creep_team1'][1]
                for tw_enemy in self.tower_team2:
                    creep.enemy_list.append(self.tower_team2[tw_enemy])
                for hero in self.hero_team2:
                    creep.enemy_list.append(self.hero_team2[hero])
                self.creep_team1[creep.id] = creep

            for i in range(1):
                creep = Creep(c_data)
                creep.pos_x = self.game_location['spawn_creep_team2'][0]
                creep.pos_y = self.game_location['spawn_creep_team2'][1]
                for tw_enemy in self.tower_team1:
                    creep.enemy_list.append(self.tower_team1[tw_enemy])
                for hero in self.hero_team1:
                    creep.enemy_list.append(self.hero_team1[hero])
                self.creep_team2[creep.id] = creep

#//// add enemy for both creep  team///
        for c1 in self.creep_team1:
            for c2 in self.creep_team2:
                self.creep_team1[c1].enemy_list.append(self.creep_team2[c2])
        for c2 in self.creep_team2:
            for c1 in self.creep_team1:
                self.creep_team2[c2].enemy_list.append(self.creep_team1[c1])

#//// add creep for all hero///
        self.update_creep_for_unit()

    def load_unit(self):
        b1 = models.building.Building.objects(name ="Base_team1").first()
        b2 =  models.building.Building.objects(name ="Base_team2").first()
        b1_data = games.GameUnit(**dict(b1.to_mongo()))
        b2_data = games.GameUnit(**dict(b2.to_mongo()))
        self.base_team1 = Building(b1_data)
        self.base_Team2 = Building(b2_data)
        tower_position =[
                    "base_left","base_right",
                    "bot_level1","bot_level2","bot_level3",
                    "mid_level1","mid_level2","mid_level3",
                    "top_level1","top_level2","top_level3"
                  ]
        if len(self.tower_team1) == 0:
            print("load Tower")
            for position in tower_position:
                t1_tw = models.Tower.objects(name = "t1_tower_"+position).first()
                t2_tw = models.Tower.objects(name = "t2_tower_"+position).first()
                t1_tw_data = games.GameUnit(**dict(t1_tw.to_mongo()))
                t2_tw_data = games.GameUnit(**dict(t2_tw.to_mongo()))
                tw1 = Tower(t1_tw_data)
                tw2 = Tower(t2_tw_data)
                self.tower_team1[tw1.id] = tw1
                self.tower_team2[tw2.id] = tw2

        #set hero and set enemy for hero
        for player in self.players:
            if player.team == "team1" and player.ready:
                if player.id in self.heros:
                    self.hero_team1[player.id] = Hero(self.heros[player.id])
                    hero = self.hero_team1[player.id]
                    for tw_enemy in self.tower_team2:
                        hero.enemy_list.append(self.tower_team2[tw_enemy])
                        self.tower_team2[tw_enemy].enemy_list.append(hero)

            elif player.team == "team2" and player.ready:
                if player.id in self.heros:
                    self.hero_team2[player.id] = Hero(self.heros[player.id],950,950)
                    hero = self.hero_team2[player.id]
                    for tw_enemy in self.tower_team1:
                        hero.enemy_list.append(self.tower_team1[tw_enemy])
                        self.tower_team1[tw_enemy].enemy_list.append(hero)

        for hero_id in self.hero_team1:
            hero = self.hero_team1[hero_id]
            for hero_enemy in self.hero_team2:
                hero.enemy_list.append(self.hero_team2[hero_enemy])
            for hero_team in self.hero_team1:
                hero.team_list.append(self.hero_team1[hero_team])
        #    print('{0}:{1}'.format(hero.name,[h.name for h in hero.enemy_list]))

        for hero_id in self.hero_team2:
            hero = self.hero_team2[hero_id]
            for hero_enemy in self.hero_team1:
                hero.enemy_list.append(self.hero_team1[hero_enemy])
            for hero_team in self.hero_team2:
                hero.team_list.append(self.hero_team2[hero_team])
         #   print('{0}:{1}'.format(hero.name,[h.name for h in hero.enemy_list]))

        print("load complete")

    def check_status_all_unit(self,time=0.001):
#//////////////check hero///////////////////////
        for hero_id in self.hero_team1:
            hero = self.hero_team1[hero_id]
            #hero.scan_enemy_unit()
            hero.count_cooldown(time)
            if hero.current_hp <= 0:
                #print('now {0} {1},{2}'.format(hero.name,hero.pos_x,hero.pos_y))
                hero.pos_x = 50
                hero.pos_y = 50
                hero.die()
                hero.countdown_to_born(time)

        for hero_id in self.hero_team2:
            #hero.scan_enemy_unit()
            hero = self.hero_team2[hero_id]
            hero.count_cooldown(time)
            if hero.current_hp <= 0:
                #print('now {0} {1},{2}'.format(hero.name,hero.pos_x,hero.pos_y))
                hero.pos_x = 970
                hero.pos_y = 970
                hero.die()
                hero.countdown_to_born(time)
#/////////////////check creep////////////////
        for creep_id in self.creep_team1:
            creep = self.creep_team1[creep_id]
            if creep.current_hp <= 0:
                creep.alive = False
                creep.pos_x = -20
                creep.pos_y = -20
                creep.stop()

        for creep_id in self.creep_team2:
            creep = self.creep_team2[creep_id]
            if creep.current_hp <= 0:
                creep.alive = False
                creep.pos_x = -20
                creep.pos_y = -20
                creep.stop()
#///////////////check tower//////////////////
        for tw_id in self.tower_team1:
            tower = self.tower_team1[tw_id]
            if tower.current_hp <= 0:
                tower.alive = False
                tower.pos_x = -200
                tower.pos_y = -200

        for tw_id in self.tower_team2:
            tower = self.tower_team2[tw_id]
            if tower.current_hp <= 0:
                tower.alive = False
                tower.pos_x = -200
                tower.pos_y = -200

    def clear_creep_died(self):
        new_dict = {}
        for creep_id in self.creep_team1:
            creep = self.creep_team1[creep_id]
            if not creep.alive:
                print('id:{0}:{1}'.format(creep.id,creep_id))
                for hero_id in self.hero_team2:
                    hero = self.hero_team2[hero_id]
                    hero.enemy_list.remove(creep)

                for tw_id in self.tower_team2:
                    tower = self.tower_team2[tw_id]
                    tower.enemy_list.remove(creep)

                for creep_id in self.creep_team2:
                    creep_op = self.creep_team2[creep_id]
                    creep_op.enemy_list.remove(creep)
            else:
                new_dict[creep_id] = creep

        self.creep_team1 = new_dict
        new_dict = {}
        for creep_id in self.creep_team2:
            creep = self.creep_team2[creep_id]
            if not creep.alive:
                print('id:{0}:{1}'.format(creep_id,creep.alive))
                for hero_id in self.hero_team1:
                    hero = self.hero_team1[hero_id]
                    hero.enemy_list.remove(creep)

                for tw_id in self.tower_team1:
                    tower = self.tower_team1[tw_id]
                    tower.enemy_list.remove(creep)

                for creep_id in self.creep_team1:
                    creep_op = self.creep_team1[creep_id]
                    creep_op.enemy_list.remove(creep)
            else:
                new_dict[creep_id] = creep
        self.creep_team2 = new_dict

    def update_creep_for_unit(self):
        for c_id in self.creep_team2:
            creep = self.creep_team2[c_id]
            for hero_id in self.hero_team1:
                hero = self.hero_team1[hero_id]
                hero.enemy_list.append(creep)
                hero.enemy_list=list(set(hero.enemy_list))
                #print('{0}: {1}'.format(hero.name,[e.name for e in hero.enemy_list]))

            for tw_id in self.tower_team1:
                tower = self.tower_team1[tw_id]
                tower.enemy_list.append(creep)
                tower.enemy_list = list(set(tower.enemy_list))

        for c_id in self.creep_team1:
            creep = self.creep_team1[c_id]
            for hero_id in self.hero_team2:
                hero = self.hero_team2[hero_id]
                hero.enemy_list.append(creep)
                hero.enemy_list=list(set(hero.enemy_list))
                #print('{0}: {1}'.format(hero.name,[e.name for e in hero.enemy_list]))

            for tw_id in self.tower_team2:
                tower = self.tower_team2[tw_id]
                tower.enemy_list.append(creep)
                tower.enemy_list = list(set(tower.enemy_list))

    def gold_per_time(self):
        for h in self.hero_team1:
            hero = self.hero_team1[h]
            hero.gold += 1

        for h in self.hero_team2:
            hero = self.hero_team2[h]
            hero.gold += 1

    def count_cooldown_skill(self,time= 0.001):
        for h in self.hero_team1:
            hero = self.hero_team1[h]
            for cd in range(0,4):
                hero.current_cooldown[cd] -= time

        for h in self.hero_team2:
            hero = self.hero_team2[h]
            for cd in range(0,4):
                hero.current_cooldown[cd] -= time

    def get_hero_team(self,team):
        if team == "team1":
            return self.hero_team1
        elif team =="team2":
           return self.hero_team2
        else:
           print("this game has not this team:{0}".format(team))

    def get_creep_team(self,team):
        if team == "team1":
            return self.creep_team1
        elif team =="team2":
           return self.creep_team2
        else:
           print("this game has not this team:{0}".format(team))

    def get_players(self):
        return self.players

    #  def run(self):
        #  for c in self.creep_team1:
            #  self.creep_team1[c].move(50,50)
        #  for c in self.creep_team1:
            #  print(str(self.creep_team1[c].pos_x) +" "+str(self.creep_team1[c].pos_y))
        #  pass

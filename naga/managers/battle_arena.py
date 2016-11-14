from .unit.hero import Hero
from .unit.tower import Tower
from .unit.building import Building
from .unit.creep import Creep
from naga import models
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
        self.nature_creep ={}
        self.scoreboard = ScoreBoard(self.hero_team1,self.hero_team2)

    def to_data_dict(self):
        dict_hero_team1 = {}
        battle_arena_data = dict(#players = self.players,
                                 #heros = self.heros,
                                 hero_team1 = self.hero_team1,
                                 hero_team2 = self.hero_team2,
                                 tower_team1 = self.tower_team1,
                                 tower_team2 = self.tower_team2,
                                 creep_team1 = self.creep_team1,
                                 creep_team2 = self.creep_team2
                            )
        return battle_arena_data

    def schedule(self):
        pass

    def create_creep(self):
        c = models.Creep.objects(name = "Creep").first()
        c_data = games.GameUnit(**dict(c.to_mongo()))
        for i in range(4):
            creep = Creep(c_data)
            self.creep_team1[creep.id] = creep
       #pass

    def load_unit(self):
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
                self.hero_team1[player.id] = Hero(self.heros[player.id])
                hero = self.hero_team1[player.id]
                for tw_enemy in self.tower_team2:
                    hero.enemy_list.append(self.tower_team2[tw_enemy])
                for hero_enemy in self.hero_team2:
                    hero.enemy_list.append(self.hero_team2[hero_enemy])
            elif player.team == "team2" and player.ready:
                self.hero_team2[player.id] = Hero(self.heros[player.id])
                hero = self.hero_team2[player.id]
                for tw_enemy in self.tower_team1:
                    hero.enemy_list.append(self.tower_team1[tw_enemy])
                for hero_enemy in self.hero_team1:
                    hero.enemy_list.append(self.hero_team1[hero_enemy])
        #print(hero.enemy_list)


 #       self.scoreboard.update()

        #self.unit_list.append()
        print("load complete")

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

    def run(self):
        for c in self.creep_team1:
            self.creep_team1[c].move(50,50)
        for c in self.creep_team1:
            print(str(self.creep_team1[c].pos_x) +" "+str(self.creep_team1[c].pos_y))
        pass

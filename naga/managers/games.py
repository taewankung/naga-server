import uuid
import datetime
import time
import json
import threading
#from threading import Timer
#import sched

from .battle_arena import BattleArena
from .unit.hero import Hero
from naga import models

class GameUnit:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def to_data_dict(self):
        return vars(self)

class GameSpace:
    def __init__(self):
        self.heros = {}

    def to_data_dict(self):
        return vars(self)


class Player:
    def __init__(self, client_id, user, token):
        self.client_id = client_id
        self.id = str(user.id)
        self.user = user
        self.token = token
        self.ready = False
        self.team = 'team1'
        self.command =dict()

    def to_data_dict(self):
        result = dict(id=self.id,
                username=self.user.username,
                ready=self.ready,
                team=self.team
                )
        return result

class GameResponse:
    def __init__(self, method, args=None, response_type='all', qos=0):
        self.response_type = response_type
        self.args = args
        self.method = method
        self.qos = qos

ROUND_CHECK = 0.001

def command_action(hero,command,naga_game):
    compleate= False
    if hero.alive:
        if command['action'] == "move":
            compleate = hero.move(command["target_pos_x"],command["target_pos_y"])
        if command['action'] == "attack":
            compleate = hero.attack(command["target"])
        if command['action'] == "use_skill":
            compleate = hero.use_skill(command["skill_num"],command["target"])
        if command['action'] == "upgrade_skill":
            compleate = hero.upgrade_skill(command["skill_num"])
        if command['action'] == "wait":
            hero.scan_enemy_unit()
            hero.scan_team_unit()
        if command['action'] == 'buy_item':
            compleate=hero.buy_item(command['item'])
        if command['action'] == 'use_item':
            compleate=hero.use_item(command['item'])
    else:
        command['action']=''
    return compleate

class GameScheduler(threading.Thread):
    def __init__(self,naga_game):
        super().__init__()
        self.naga_game = naga_game
        self.status = 'wait'
        self.counter_send =0
        self.lock = threading.Lock()
        self.old_event ={}

    def run(self):
        for p in self.naga_game.players:
            self.old_event[p.id] = ''
        while self.status != 'stop':
            self.counter_send = 0
            for p in self.naga_game.players:
                if len(p.command) !=0:
                    self.execute(p,p.command)
            time.sleep(ROUND_CHECK)

    def stop(self):
        self.status = 'stop'

    def execute(self,player,command):
        if player.id in self.naga_game.game_space.hero_team1:
            hero = self.naga_game.game_space.hero_team1[player.id]
        elif player.id in self.naga_game.game_space.hero_team2:
            hero = self.naga_game.game_space.hero_team2[player.id]
        if hero.act_status["found_event"] !="" and self.old_event[player.id] != hero.act_status["found_event"]:
            args = dict(msg=hero.act_status["found_event"])
            response = GameResponse(method='complete_command',
                                    response_type='owner',
                                    args=args,
                                    qos=1)
            self.naga_game.game_controller.response(
                                    response,
                                    player.client_id,
                                    self.naga_game
                                    )
            many_send_list = ['can not buy item','battle','can not use item']
            if hero.act_status["found_event"] not in  many_send_list:
                self.old_event[player.id] = hero.act_status["found_event"]
                hero.act_status["found_event"]=""
            else:
                self.old_event[player.id] = hero.act_status["found_event"]

        if command_action(hero,command,self.naga_game):
            args = dict(msg=command["msg"])
            print(player.client_id+" "+command["msg"])
            response = GameResponse(method='complete_command',
                                    response_type='owner',
                                    args=args,
                                    qos=1)
            self.naga_game.game_controller.response(
                                    response,
                                    player.client_id,
                                    self.naga_game
                                    )
            print(player.command)
            player.command =dict(action='wait')
            hero.act_status['action'] = 'wait'
        single_use_list = ['use_skill','buy_item','use_item']
        if player.command in single_use_list:
            player.command = dict(action='wait')
        #  self.lock.release();

class NagaGame(threading.Thread):
    def __init__(self, room_id, room_name, owner,game_controller):
        super().__init__()
        self.status = 'wait'
        self.room_id = room_id
        self.room_name = room_name
        self.players = []
        self.game_space = BattleArena(self.players)#GameSpace()
        self.owner = owner
        self.ready_time = None
        self.game_controller = game_controller
        self.game_scheduler = GameScheduler(self)
        self.lock = threading.Lock()
        self.spawn_time = 0
        self.gold_timer = 0
 #       self.start_time = time.time()
        self.player_executors = dict()

    def run(self):
        count = 0
        status = ''
#        print('check')
        while self.status != 'stop':
            if self.status == 'play':
                if count ==0:
                    self.game_scheduler.start()
                    self.spawn_time=time.time()
                    self.gold_timer=time.time()
                    count = count+1

#///////////////Spawn Creep//////////////////////
                if time.time()-self.spawn_time > 30:
                    self.spawn_time = time.time()
                    print('create_creep')
                    self.game_space.create_creep('mid')
                    self.game_space.create_creep('btm')
                    self.game_space.create_creep('top')
#                else:
#                    self.spawn_time = self.spawn_time + ROUND_CHECK
#                    print('{0}'.format(time.time()- self.spawn_time))
#///////////////Creep Action////////////////////
                for creep_id in self.game_space.creep_team1:
                    creep = self.game_space.creep_team1[creep_id]
                    creep.run_behavior(lane=str(creep.position_lane)+'_team1')

                for creep_id in self.game_space.creep_team2:
                    creep = self.game_space.creep_team2[creep_id]
                    creep.run_behavior(lane=str(creep.position_lane)+'_team2')
                    #print(creep.position_lane)
#///////////////Tower Action////////////////////
                for tw_id in self.game_space.tower_team2:
                    tower = self.game_space.tower_team2[tw_id]
                    tower.update_enemy()
                    tower.attack()

                for tw_id in self.game_space.tower_team1:
                    tower = self.game_space.tower_team1[tw_id]
                    tower.update_enemy()
                    tower.attack()
#///////////////Base ////////////////////////////
                if self.game_space.base_team1 is not None and not self.game_space.base_team1.alive:
                    self.status = 'team2 win'
                elif self.game_space.base_team2 is not None and not self.game_space.base_team2.alive:
                    self.status = 'team1 win'
#///////////////Update Game/////////////////////
                self.game_space.check_status_all_unit(ROUND_CHECK)
                if time.time()-self.gold_timer >=1:
                    self.gold_timer = time.time()
                    self.game_space.gold_per_time()
                self.game_space.clear_creep_died()
                self.game_controller.response_all(self.update_game(),self)
            time.sleep(ROUND_CHECK)
        print('End Game')
        response = GameResponse(method='end_game',
                                args=dict(msg =self.status),
                                response_type='owner',
                                qos=1
                               )
        self.game_controller.response_all(response,self)
        self.status = 'stop'
        self.game_scheduler.stop()
#        self.stop()
#            now = time.time()
#            print('time.time:{}'.format(now-self.start_time))

    def update(self, request):
        print("update", request)

    def spawn_creep(self):
        self.game_space.create_creep()
        print("spawn")
        #self.game_controller.response_all(self.update_game(),self)

    def ready(self, request):
        player = request['player']
        player.ready = True
        player_ready_count = len([p for p in self.players if p.ready])

        print("ready count:", player_ready_count)
        self.ready_time = datetime.datetime.now()
        self.game_space.load_unit()
        if player_ready_count != len(self.players):
            return
        #if self.status != '':
        self.status = 'play'

        response = GameResponse(method='start_game', qos=1)
        return response

    def add_player(self, player):
        self.players.append(player)


    def update_game(self):
        args = dict(game_space=self.game_space)
        response = GameResponse(method='update_game',
                args= args,
                response_type='owner',
                qos=1)
        return response

    def initial(self, request):
        player = request['player']
        print("################")
        print(request["client_id"])
        print("################")
        args = dict(players=self.players, player=player, game_space=self.game_space)
        response = GameResponse(method='initial_game',
                args=args,
                response_type='owner',
                qos=1)
        return response

    def stop(self,request):
        self.game_scheduler.stop()
        self.game_controller.response_all(self.update_game(),self)
        self.status = 'stop'
        response = GameResponse(method='end_game',
                                args=dict(msg =self.status),
                                response_type='owner',
                                qos=1
                               )
        self.game_controller.response_all(response,self)


    def buy_item(self,request):
        params = request['args']
        player_r = request['player']
        msg = params['msg']
        item = params['item']
        if player_r.id in self.game_space.hero_team1:
            hero = self.game_space.hero_team1[player_r.id]
        if player_r.id in self.game_space.hero_team2:
            hero = self.game_space.hero_team2[player_r.id]
        for p in self.players:
            if p.client_id == player_r.client_id:
                p.command =dict(action="buy_item",
                                #current_pos=(hero.pos_x,hero.pos_y),
                                item = self.game_space.item_shop[item],
                                msg=msg
                                )
                hero.act_status['action'] = 'buy item: {}'.format(item)

    def use_item(self,request):
        params = request['args']
        player_r = request['player']
        msg = params['msg']
        item = params['item']
        if player_r.id in self.game_space.hero_team1:
            hero = self.game_space.hero_team1[player_r.id]
        if player_r.id in self.game_space.hero_team2:
            hero = self.game_space.hero_team2[player_r.id]
        for p in self.players:
            if p.client_id == player_r.client_id:
                p.command =dict(action="use_item",
                                #current_pos=(hero.pos_x,hero.pos_y),
                                item = self.game_space.item_shop[item],
                                msg=msg
                                )
                hero.act_status['action'] = 'use item: {}'.format(item)

    def use_skill(self,request):
        params = request['args']
        msg = params['msg']
        skill_num = params['skill_num']
        player_r = request['player']
        target = params['target']
        if player_r.id in self.game_space.hero_team1:
            hero = self.game_space.hero_team1[player_r.id]
        if player_r.id in self.game_space.hero_team2:
            hero = self.game_space.hero_team2[player_r.id]
        for p in self.players:
            if p.client_id == player_r.client_id:
                p.command =dict(action="use_skill",
                                #current_pos=(hero.pos_x,hero.pos_y),
                                skill_num = skill_num,
                                target= target,
                                msg=msg
                                )
                hero.act_status['action'] = 'use skill: {}'.format(skill_num)

    def move_hero(self, request):
        #self.lock.acquire()
        params = request['args']
        msg = params['msg']
#        print(request)
        x = params['x']
        y = params['y']
        player_r = request['player']
        if player_r.id in self.game_space.hero_team1:
            hero = self.game_space.hero_team1[player_r.id]
            hero.act_status['action']='move'
        elif player_r.id in self.game_space.hero_team2:
            hero = self.game_space.hero_team2[player_r.id]
            hero.act_status['action']='move'
        for p in self.players:
            if p.client_id == player_r.client_id:
                p.command =dict(action="move",
                                #current_pos=(hero.pos_x,hero.pos_y),
                                target_pos_x=x,
                                target_pos_y=y,
                                target="",
                                msg=msg
                                )
        #self.lock.release();

    def attack(self,request):
        target_enemy = request["args"]["target"]
        msg = request['args']['msg']
        player_r = request['player']
        if target_enemy != {}:
            #print(str(request["player"].id)+ " will attack:"+str(target_enemy["name"]))
            for p in self.players:
                if p.client_id == player_r.client_id:
                    p.command = dict(action="attack",
                                     target=str(target_enemy),
                                     msg=msg
                                    )

    def alliance_message(self,request):
        params = request['args']
        player_r = request['player']
        msg_to_team = params['msg_to_team']
        args = dict(msg=msg_to_team
                   )
        for p in self.players:
            if p.team == player_r.team and player_r.client_id != p.client_id:
                print('from {0} to {1}:{2}'.format(player_r.id,p.id,msg_to_team))
                response = GameResponse(method='complete_command',
                                response_type='owner',
                                args=args,
                                qos=1)
                self.game_controller.response(
                                            response,
                                            p.client_id,
                                            self
                                            )

    def upgrade_skill(self,request):
        params = request['args']
        player_r = request['player']
        msg = params['msg']
        skill_num = params['skill_num']
        for p in self.players:
            if p.client_id == player_r.client_id:
                p.command = dict(action="upgrade_skill",
                                 skill_num = skill_num,
                                 msg=msg
                                )

    def to_data_dict(self):
        result = dict(status=self.status,
                    room_id=self.room_id,
                    room_name=self.room_name,
                    owner=self.owner,
                    players=[str(p.user.id) for p in self.players if p.user],
                    game_space=self.game_space
                )
        return result

    def to_json(self):
        result = self.to_data_dict()
        result_json = json.dumps(result)
        return result_json

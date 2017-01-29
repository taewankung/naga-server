from .base import Manager
from naga import models
import uuid
import datetime
import json
from naga.game_controller import GameStatusController
from .base import ComplexEncoder

from .games import NagaGame, Player ,GameUnit

class Room(Manager):
    def __init__(self, mqtt_client):
        super().__init__(mqtt_client)
        self.rooms = dict()
        self.status = 'wait'

    def create_room(self, request):
        room_name = None
        args = request.get('args')
        print(request)
        print(request)
        if args:
            room_name = args.get('room_name')
        room_id = str(uuid.uuid4())
        user = self.get_user(request)
        print('created')
        game_controller = GameStatusController(self.mqtt_client,self)
        game_status = NagaGame(room_id, room_name, user,game_controller)
        game_status.players.append(Player(request['client_id'], user, request['token']))

        self.rooms[room_id] = game_status
        game_status.start()
        print('game status is ', game_status.to_data_dict())
        return game_status.to_data_dict()

    def join_game(self, request):
        print("Join Game")
        room_id = request['args'].get('room_id', None)
        #print(room_id)
        response = dict()
        game = self.rooms.get(room_id, None)
        print(request)
        if game:
            if len(game.players) <= 10:
                user = self.get_user(request)
                args=dict()
                check = False
                for p in game.players:
                    print(user)
                    print(p.user)
                    if user == p.user:
                        print(request['client_id'])
                        check = True
                        # remove if deploy
                        p.client_id = request['client_id']
                        break

                if not check:
                    player = Player(request['client_id'], user, request['token'])
                    if len(game.players) % 2 != 0:
                        player.team = 'team2'
                    game.add_player(player)
                response['joined'] = True
                response['room_id'] = room_id
                response['response_type'] = 'all_in_room'
            else:
                self.status ='Full'
                response['joined'] = False
        else:
            response['joined'] = False

        return response

    def list_rooms(self, request):
        rooms = []
        for room_id, room in self.rooms.items():
            if room.status == 'wait':
                rooms.append((room_id,room))

        response = dict(rooms=rooms)
        return response

    def list_players(self, request):
        players = []
        room_id = request['args'].get('room_id', None)

        if room_id is None:
            return

        room = self.rooms.get(room_id, None)
        if room is None:
            return

        players = room.players
        #print('check players')
        response = dict(players=players)

        return response

    def select_hero(self, request):
        print('select hero request', request)
        hero_name = request['args'].get('hero', None)
        print(hero_name)
        room_id = request['args'].get('room_id', None)
        game = self.rooms.get(room_id, None)
        hero = models.Hero.objects(name=hero_name).first()

        user = self.get_user(request)

        if hero is  None:
            return


        gu = GameUnit(**dict(hero.to_mongo()))
        game.game_space.heros[str(user.id)] = gu

#        print(game.heros)
        response = dict()
        return response

    def disconnect_room(self,request):
        room_id = request['args'].get('room_id', None)
        client_id = request['client_id']

        game = self.rooms.get(room_id, None)

        if game:
            for player in game.players:
                if player.client_id == client_id:
                    game.players.remove(player)

            if len(game.players) == 0:
                r = self.rooms.pop(room_id)
                r.stop()

        response = dict()
        return response

    def start_game(self, request):
        room_id = request['args'].get('room_id', None)
        game = self.rooms.get(room_id, None)
        game.status = 'play'
        game.start()

        return dict(status='play')


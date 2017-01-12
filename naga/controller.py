# import json

from . import managers
from . import game_controller

class NagaController:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
#       self.api = managers.api_game
        self.user = managers.User(self.mqtt_client)
        self.room = managers.Room(self.mqtt_client)

        self.game_controller = game_controller.GameStatusController(self.mqtt_client, self.room)
        self.game_controller.start()

        # comment if release
        from .managers.rooms import NagaGame, Player, GameUnit
        from naga import models
        test_room_id = 'test_room_id'
        u = models.User.objects(username='test').first()
        game = NagaGame(test_room_id, 'test_room_name', u, self.game_controller)

        p1 =  Player('test_client_id', u, 'test_token')

        u2 = models.User.objects(username='client1').first()
        p2 = Player('client1', u2, 'client1')
        p2.team ='team2'
#        u3 = models.User.objects(username='client3').first()
#        p3 = Player('client3', u3, 'client3')

#        game.add_player(p3)
        game.add_player(p2)
        game.add_player(p1)

        self.room.rooms[test_room_id] = game
        hero = models.Hero.objects(name='Sinsamut').first()
        hero2 = models.Hero.objects(name='Apaimanee').first()
        hero2_unit = GameUnit(**dict(hero2.to_mongo()))

        hero2_unit.pos_x = 950
        hero2_unit.pos_y = 950
        game.game_space.heros[str(u.id)] = GameUnit(**dict(hero.to_mongo()))
        game.game_space.heros[str(u2.id)] = hero2_unit
#game.game_space.heros[str(u3.id)] = GameUnit(**dict(hero.to_mongo()))
        game.start()

    def stop(self):
        self.game_controller.stop()

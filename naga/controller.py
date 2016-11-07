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
        #  print(p1.id)

        u2 = models.User.objects(username='client1').first()
        p2 = Player('client1', u2, 'client1')

        #  u3 = models.User.objects(username='client1').first()
        #  p3 = Player('client1', u2, 'client2')

        #  u4 = models.User.objects(username='client1').first()
        #  p4 = Player('client1', u2, 'client3')

        #  u5 = models.User.objects(username='client1').first()
        #  p5 = Player('client1', u2, 'client4')

#        print(p2.id)
        game.add_player(p2)
        game.add_player(p1)

        self.room.rooms[test_room_id] = game
        hero = models.Hero.objects(name='Sinsamut').first()
        hero2 = models.Hero.objects(name='Apaimanee').first()
        game.game_space.heros[str(u.id)] = GameUnit(**dict(hero.to_mongo()))
        game.game_space.heros[str(u2.id)] = GameUnit(**dict(hero.to_mongo()))
        game.start()
#       game.game_space.load_unit()
#       game.game_space.get_players_in_team("team1")

    def stop(self):
        self.game_controller.stop()

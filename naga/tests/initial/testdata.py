from naga import models

from naga.initial.heroes import DataHero
from naga.initial.buildings import DataBuilding
#from apmn_server.initial.items import DataItem
from naga.initial.towers import DataTower
from naga.initial.creeps import DataCreep
import os
import sys

class DataHeroTest():
    def __init__(self):

        settings = {
                    'mongodb.db_name':'naga',
                    'mongodb.host': 'localhost'
                    }
        models.initial(settings)

    def test_load(self):
        d = None
        if len(sys.argv) == 1:
            d = DataHero('../../..')
        else:
            d = DataHero(sys.argv[1])

        d.load()
class DataCreepTest():
    def __init__(self):

        settings = {
                    'mongodb.db_name':'naga',
                    'mongodb.host': 'localhost'
                    }
        models.initial(settings)

    def test_load(self):
        d = None
        if len(sys.argv) == 1:
            d = DataCreep('../../..')
        else:
            d = DataCreep(sys.argv[1])

        d.load()

class DataTowerTest():
    def __init__(self):

        settings = {
                    'mongodb.db_name':'naga',
                    'mongodb.host': 'localhost'
                    }
        models.initial(settings)

    def test_load(self):
        d = None
        if len(sys.argv) == 1:
            d = DataTower('../../..')
        else:
            d = DataTower(sys.argv[1])

        d.load()


class DataBuildingTest():
    def __init__(self):

        settings = {
                    'mongodb.db_name':'naga',
                    'mongodb.host': 'localhost'
                    }
        models.initial(settings)

    def test_load(self):
        d = None
        if len(sys.argv) == 1:
            d = DataBuilding('../../..')
        else:
            d = DataBuilding(sys.argv[1])

        d.load()

if __name__ == '__main__':
    data_hero_test = DataHeroTest()
    data_creep_test = DataCreepTest()
    data_tower_test = DataTowerTest()
    data_building_test = DataBuildingTest()

    data_hero_test.test_load()
    data_creep_test.test_load()
    data_tower_test.test_load()
    data_building_test.test_load()

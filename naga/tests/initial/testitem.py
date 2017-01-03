from naga import models

from naga.initial.items import DataItem
#from apmn_server.initial.items import DataItem
import os
import sys

class DataItemTest():
    def __init__(self):

        settings = {
                    'mongodb.db_name':'naga',
                    'mongodb.host': 'localhost'
                    }
        models.initial(settings)

    def test_load(self):
        d = None
        if len(sys.argv) == 1:
            d = DataItem('../../..')
        else:
            d = DataItem(sys.argv[1])

        d.load()

if __name__ == '__main__':
    data_item_test = DataItemTest()
    data_item_test.test_load()

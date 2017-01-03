
from naga import models
import os
import json


class DataItem():
    def __init__(self, home_path):
        self.home_path = home_path
        self.item_data_path = home_path + '/data/items'

    def load(self):
        print(self.item_data_path)
        print (os.listdir(self.item_data_path))
        for filepath in os.listdir(self.item_data_path):
            print (filepath)
            fp = open(self.item_data_path+'/'+filepath, 'r')
            item_dict = json.load(fp)
            print(item_dict)
            item = models.Item.objects(name=item_dict['name']).first()
            if item:
                item.update(**item_dict)
            else:
                item = models.Item(**item_dict)
            item.save()

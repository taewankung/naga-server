from .sensor import Sensor
from operator import itemgetter
import math
class TeamSensor(Sensor):
    def __init__(self,unit,unit_list):
        super().__init__(unit,unit_list)

    def scan(self,in_range = 50):
        unit_in_range = list()
        near_list = list()
        #u is unit
#        print(self.unit_list)
        for u in self.unit_list:
            dist_u = math.sqrt(
                          pow((u.pos_x - self.unit.pos_x),2)+
                          pow((u.pos_y - self.unit.pos_y),2)
                          )
            if dist_u <= in_range:
                near_list.append((u,dist_u))
                unit_in_range.append(u)
                near_list = sorted(near_list,key=itemgetter(1))

        for i in range(0,len(near_list)):
            unit_in_range[i] = near_list[i][0]
        #print('{0}:{1}'.format(self.unit.name,[u.name for u in unit_in_range]))
        return unit_in_range

    def update_unit_list(self):
        self.unit_list = self.unit.enemy_list
        pass

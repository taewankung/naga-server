from .sensor import Sensor
import math
class EnemySensor(Sensor):

    def __init__(self,unit,unit_list):
        super().__init__(unit,unit_list)

    def scan(self,in_range = 50):
        unit_in_range = list()
        #u is unit
        for u in self.unit_list:
            dist_u = math.sqrt(
                          pow((u.pos_x - self.unit.pos_x),2)+
                          pow((u.pos_y - self.unit.pos_y),2)
                          )
            if dist_u <= in_range:
                if u not in unit_in_range:
                    unit_in_range.append(u)
            else:
                if u in unit_in_range:
                    unit_in_range.remove(u)
        return unit_in_range

    def update_unit_list(self):
        self.unit_list = self.unit.enemy_list
        pass

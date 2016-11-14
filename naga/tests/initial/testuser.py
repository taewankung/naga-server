from naga import models

import datetime

class UserTest:
    def __init__(self):
        settings = {
                    'mongodb.db_name':'naga',
                    'mongodb.host': 'localhost'
                    }
        models.initial(settings)

    def initial(self):
        u = models.User.objects(username='clinet4').first()
        if not u:
            #  u = models.User(username='test', email='test@naga.local',
                            #  first_name='testfirst', last_name='testlast')
            #  u.set_password('testpasswd')
            #  u.save()
            u1 = models.User(username='client4', email='client4@naga.local',
                      	  first_name='client4first', last_name='client4last')
            u1.set_password('client4')
            u1.save()


if __name__ == '__main__':
    ut = UserTest()
    ut.initial()

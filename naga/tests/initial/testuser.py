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
        u = models.User.objects(username='test').first()
        if not u:
            u = models.User(username='test', email='test@naga.local',
                      	  first_name='testfirst', last_name='testlast')
            u.set_password('testpasswd')
            u.save()

if __name__ == '__main__':
    ut = UserTest()
    ut.initial()

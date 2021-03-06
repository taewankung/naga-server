from .base import Manager
from naga import models

import datetime

class User(Manager):
    def login(self, request):
        print('check login')
        args = request.get('args')
        username = args.get('username')
        password = args.get('password')


        response = dict()

        user = models.User.objects(username=username, password=models.User.hash_password(password)).first()

        if user:
            response['loggedin'] = True
            last_login = models.LastLogin(user=user)
            last_login.save()

            token = models.Token(user=user)
            token.accessed_date = datetime.datetime.now()
            token.expired_date = token.accessed_date + datetime.timedelta(days=1)
            token.save()
            token.reload()

            response['token'] = str(token.id)


        else:
            response['loggedin'] = False

        print(response)

        return response

    def register(self, request):
        args = request.get('args')

        username = args.get('username')
        password = args.get('password')
        email = args.get('email')
        first_name = args.get('first_name')
        last_name = args.get('last_name')

        user = models.User(username=username,
                email=email,
                first_name=first_name,
                last_name=last_name)
        user.set_password(password)
        user.save()
        user.reload()


        response = dict()
        if hasattr(user, 'id'):
            response['registed'] = True
        else:
            response['registed'] = False

        return response


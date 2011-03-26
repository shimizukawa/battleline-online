from os import environ

def gae_login(email='test@example.com', admin=False):
    environ['USER_EMAIL'] = environ['USER_ID'] = email
    environ['USER_IS_ADMIN'] = '1'


def gae_logout():
    if 'USER_EMAIL' in environ:
        del environ['USER_EMAIL']
    if 'USER_ID' in environ:
        del environ['USER_ID']
    if 'USER_IS_ADMIN' in environ:
        del environ['USER_IS_ADMIN']


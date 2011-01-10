# -*- coding: utf-8 -*-

from google.appengine.api import users
from controller_base import *
from app.models import *
from lib.hooks import hook

__all__ = ['ApplicationController', 'StopRequestProcess']


class ApplicationController(ControllerBase):

    @hook('before')
    def setup_params(self):
        v = self._v
        u = users.get_current_user()
        v.user = GameUser.playing_users().filter('user =',u).get()
        if v.user:
            v.game = v.user.game


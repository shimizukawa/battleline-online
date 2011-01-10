# -*- coding: utf-8 -*-

from google.appengine.api import users
from lib.controllers.controller_base import ControllerBase
from lib.hooks import hook
from app.models import GameUser

__all__ = ['ApplicationController']


class ApplicationController(ControllerBase):

    @hook('before')
    def setup_params(self):
        v = self._v
        u = users.get_current_user()
        v.user = GameUser.playing_users().filter('user =',u).get()
        if v.user:
            v.game = v.user.game


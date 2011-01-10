# -*- coding: utf-8 -*-
from google.appengine.api import users
from app.controllers.controller import ApplicationController
from app.models.game import Game

class GameController(ApplicationController):

    def create(self, *args):
        g = Game()
        g.put()
        self.redirect('/lobby')

    def join(self, game_key):
        u = users.get_current_user()
        if not u:
            return self.redirect('/lobby')

        g = Game.get(game_key)
        if u in (x.user for x in g.users):
            # ���[�U�[�͑Ώۂ̃Q�[���ɎQ�����Ȃ̂ŁA�������Ȃ�
            pass
        elif g.is_joinnable:
            # ���[�U�[�͑Ώۂ̃Q�[���ɎQ�������Ă��Ȃ����A�Q���\�Ȃ̂ŁA
            # ���[�U�[���Q�[���ɒǉ�����B
            gu = g.create_user(u)
            gu.put()
        else:
            # ���[�U�[�͂��̃Q�[���ɎQ���o���Ȃ�
            return self.redirect('/lobby')

        return self.redirect('/lobby/waiting/')


def main():
    from google.appengine.ext import webapp
    from google.appengine.ext.webapp.util import run_wsgi_app

    application = webapp.WSGIApplication([
        #('^/game(/?$|.*$)', GameController),
        ('^/game/([^/]*)$', GameController),
        ('^/game/([^/]*)/(.*)$', GameController),
    ])
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

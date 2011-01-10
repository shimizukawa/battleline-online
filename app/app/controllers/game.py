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
            # ユーザーは対象のゲームに参加中なので、何もしない
            pass
        elif g.is_joinnable:
            # ユーザーは対象のゲームに参加中していないが、参加可能なので、
            # ユーザーをゲームに追加する。
            gu = g.create_user(u)
            gu.put()
        else:
            # ユーザーはこのゲームに参加出来ない
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

# -*- coding: utf-8 -*-
from google.appengine.api import users
from app.controllers.controller import ApplicationController
from app.models.game import GameUser
from app.models.round import Round

class LobbyController(ApplicationController):

    def index(self, *args):
        self.render('index.html')

    def waiting(self, *args):
        u = users.get_current_user()
        if not u:
            return self.redirect('/lobby')

        gu = GameUser.playing_users().filter('user =', u).get()
        if gu is None:
            return self.redirect('/lobby')
        g = gu.game
        if g.users.count() == 1:
            pass
        elif g.users.count() == 2:
            r = Round.create(g)
            r.put()
            g.start()
            g.put()
            #return self.redirect(self.get_url('PlayGame'))
            return self.redirect('/play/')
        else:
            raise RuntimeError('trying to start game, but user count is invalid.')

        return self.render('waiting.html')


def main():
    from google.appengine.ext import webapp
    from google.appengine.ext.webapp.util import run_wsgi_app

    application = webapp.WSGIApplication([
        ('^/lobby', LobbyController),
        ('^/lobby/([^/]*)(/.*)?$', LobbyController),
    ])
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

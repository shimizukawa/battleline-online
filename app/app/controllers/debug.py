# -*- coding: utf-8 -*-
from app.controllers.controller import ApplicationController
from app.models.game import Game

class DebugController(ApplicationController):
    def logout_user(self, *args, **kw):
        raise NotImplementedError('logout_user')
        #user = User.find(params[:user_id])
        #user.state = 'LOGOUT'
        #user.save
        #redirect_to :controller => :home, :action => :index 

    def close_game(self, game_key):
        game = Game.get(game_key)
        game.close()
        game.put()
        #from app.controllers.main import MainPage
        #self.redirect(self.get_url(MainPage))
        #self.redirect(self.get_url('app.controllers.main.MainPage'))
        self.redirect('/lobby')


def main():
    from google.appengine.ext import webapp
    from google.appengine.ext.webapp.util import run_wsgi_app

    application = webapp.WSGIApplication([
        ('^/debug/([^/]*)$', DebugController),
        ('^/debug/([^/]*)/(.*)$', DebugController),
    ])
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

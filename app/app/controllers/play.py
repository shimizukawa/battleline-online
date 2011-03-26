# -*- coding: utf-8 -*-
from google.appengine.api import users
from gaefw.hooks import hook
from gaefw.controllers.controller_base import StopRequestProcess
from app.controllers.controller import ApplicationController
#from app.models.game import Game, GameUser
#from app.models.round import Round

def render_card(card, front=True):
    card = card.resolve(context)
    output = nodelist.render(context)
    return output


class PlayController(ApplicationController):
    hooks = ApplicationController.hooks.copy()

    @hook('before')
    def check_user(self):
        if not self._v.user:
            #self.redirect(self.get_url('MainPage'))
            self.redirect('/')
            raise StopRequestProcess()

    @hook('before')
    def setup_round(self):
        game = self._v.game
        self._v.round = game and game.rounds.order('-turn').get() or None

    def index(self, *args):
        vars = dict(
            flash = {},
            render_card = render_card
        )
        self.render('index.html', vars)



def main():
    from google.appengine.ext import webapp
    from google.appengine.ext.webapp.util import run_wsgi_app

    application = webapp.WSGIApplication([
        ('^/play', PlayController),
        ('^/play/([^/]*)$', PlayController),
        ('^/play/([^/]*)/(.*)$', PlayController),
    ])

    from google.appengine.ext.appstats import recording
    application = recording.appstats_wsgi_middleware(application)

    run_wsgi_app(application)

if __name__ == "__main__":
    main()

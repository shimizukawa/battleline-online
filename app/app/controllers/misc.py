# -*- coding: utf-8 -*-
from app.controllers.controller import ApplicationController

class MiscController(ApplicationController):

    def index(self, *args):
        return self.redirect('/lobby')


def main():
    from google.appengine.ext import webapp
    from google.appengine.ext.webapp.util import run_wsgi_app

    application = webapp.WSGIApplication([
        ('^/', MiscController),
    ])
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

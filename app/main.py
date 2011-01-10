# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import lib.templatetags

from app.controllers import *

urls = [
    ('^/$', MainPage),
#    ('^/(create)/$', MainPage),
#    ('^/(join)/(.+)$', MainPage),
#    ('^/(waiting)/$', MainPage),
#    ('^/(watch)/(.+)$', MainPage),
#    ('^/play/', PlayController),
#    ('^/debug/(close_game)/(.+)$', DebugController),
#    ('^/debug/(logout_user)/(.+)$', DebugController),
]

application = webapp.WSGIApplication(urls, debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


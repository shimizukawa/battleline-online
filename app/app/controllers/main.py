# -*- coding: utf-8 -*-

from google.appengine.api import users

from controller import *
from app.models import *

__all__ = ['MainPage']


class MainPage(ApplicationController):

    def index(self, *args):
        self.render('index.html')

    def create(self, *args):
        g = Game()
        g.put()
        self.redirect('/')

    def join(self, game_key):
        u = users.get_current_user()
        if not u:
            return self.redirect('/')

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
            return self.redirect('/')
  
        return self.redirect('/waiting/')

    def waiting(self, *args):
        u = users.get_current_user()
        if not u:
            return self.redirect('/')

        gu = GameUser.playing_users().filter('user =', u).get()
        if gu is None:
            return self.redirect('/')
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

    def watch(self, *args):
        raise NotImplementedError('watch')
#        redirect_to :controller => :play, :action => :debug 



# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import users
from lib.utils import *

__all__ = ['Game', 'GameUser']


class Game(db.Model):
    state = db.StringProperty(required=True, default='NEW')
    stage = db.IntegerProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    # as named scope...
    rounds = property(lambda s:s.round_set)
    active = classmethod(lambda s:s.all().filter("state in",('NEW','OPEN')))
    # named_scope :joined, lambda {|user| {:joins=>"inner join game_users on games.id=game_users.game_id", :conditions=>["game_users.user_id = ?", user.id]}}
    #users = property(lambda s:s.gameuser_set)
    @property
    def users(self):
        if self.is_saved():
            return self.gameuser_set
        return ()

    def __init__(self, *args, **kw):
        setdefault(kw, 'stage', Game.all().count() + 1)
        super(Game, self).__init__(*args, **kw)

    def __users_state_update(self):
        for u in self.users:
            u._state = self.state
        db.put(self.users)

    def create_user(self, user):
        return GameUser(parent=self, game=self, user=user)

    def start(self):
        self.state = 'OPEN'

    def close(self):
        self.state = 'CLOSED'

    def put(self, *args, **kw):
        f = super(Game, self).put(*args, **kw)
        self.__users_state_update()
        return f

        #def txn(users, *args, **kw):
        #    f = super(Game, self).put(*args, **kw)
        #    for ukey in users:
        #        u = db.get(ukey)
        #        u.put()
        #    return f
        #return db.run_in_transaction(txn, obj2key(self.users), *args, **kw)

    @property
    def is_started(self):
        return self.state != 'NEW'

    @property
    def is_closed(self):
        return self.state == 'CLOSED'

    @property
    def is_playing(self):
        return self.state == 'OPEN'

    @property
    def winner(self):
        r = self.rounds.order('-turn').get()
        if r:
            return r.winner

    @property
    def is_joinnable(self):
        user = users.get_current_user()
        if self.users.count(2) < 2:
            return True
        elif user in self.users:
            return True
        else:
            return False

    @property
    def turn(self):
        if self.rounds.count() == 0:
            return 0
        return self.rounds.order('-created_at').get().turn


class GameUser(db.Model):
    user = db.UserProperty(required=True)
    game = db.ReferenceProperty(Game, required=True)
    _state = db.StringProperty(required=True, default='NEW')
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    # as named scope...
    #playing_users = classmethod(lambda s:s.all().filter('game.state !=','CLOSED'))
    playing_users = classmethod(lambda s:s.all().filter('_state !=','CLOSED'))

    @property
    def state(self):
        return self._state

    @property
    def is_playing(self):
        return self.game.is_playing

    def __str__(self):
        return self.user.nickname()

    def __unicode__(self):
        return self.user.nickname()


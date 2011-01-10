# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import users
import random
from lib.utils import *
from game import *
from card import *
from state import *

__all__ = ['Round','RoundProcess','Line','Player']


class Round(db.Model):
    game = db.ReferenceProperty(Game, required=True)
    turn = db.IntegerProperty(required=True, default=0)
    flags = db.ListProperty(int, default=[-1]*9) # Player.key
    _troops = db.ListProperty(db.Key) # TroopCard
    _tactics = db.ListProperty(db.Key) # TacticsCard
    _discards = db.ListProperty(db.Key) # Card
    state = db.StringProperty(required=True, default='StartState') # State class's name # TODO: can't set class object
    current_side = db.IntegerProperty(default=0, required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)

    # wrapper
    troops = ListPropertyAccessor('_troops')
    tactics = ListPropertyAccessor('_tactics')
    discards = ListPropertyAccessor('_discards')

    # like named_scope ...
    process = property(lambda s:s.roundprocess_set)
    process_get = lambda s,state:s.process.filter('state =',state).get()
    players = property(lambda s:s.player_set.order('side'))
    players_s = lambda s,side:s.players.filter('side =',side).get()
    current_player = property(lambda s:s.players_s(s.current_side))
    defence_player = property(lambda s:s.players_s(s.defence_side))

#     validate :validate_fields

    @staticmethod
    def create(game):
        def create_txn(game_key, user_keys):
            r = Round(game=game_key)
            #r.put()
            db.put(r)
            for side in range(2):
                p = Player(parent=r, round=r, side=side, user=user_keys[side])
                p.put()
                for line in range(9):
                    l = Line(parent=p, player=p, num=line)
                    l.put()
            return r

        def initialize_txn(round, players, troops, tactics):
            r = db.get(round)
            # troops
            random.shuffle(troops)
            r._troops = troops

            # tactics
            random.shuffle(tactics)
            r._tactics = tactics

            # hands
            for p in key2obj(players):
                h = []
                for c in range(7):
                    h.append(r._troops.pop(0))
                p._hand = sorted(h)
                p.put()
            #r.put()
            db.put(r)
            return r

        user_keys = obj2key(game.users)
        r = db.run_in_transaction(create_txn, game.key(), user_keys)
        if game.rounds.count() == 1:
            troops = Card.create_troops()
            tactics = Card.create_tactics()
            r = db.run_in_transaction(initialize_txn, r.key(),
                                      obj2key(r.players),
                                      obj2key(troops), obj2key(tactics))
        return r

    def __init__(self, *args, **kw):
        ## FIXME!! current_side is set to 0 always.
        #setdefault(kw, 'current_side', random.randint(0,1000) % 2)
        super(Round, self).__init__(*args, **kw)

    def play_card(card, to):
        self.state.process(card, to)

    def setup_tactics(card, to):
        self.state.process(card, to)

    def drow_troop(self):
        self.state.process('TROOP')

    def drow_tactics(self):
        self.state.process('TACTICS')

    def proof(line):
        self.state.process('PROOF', line)

    def judge(agree):
        self.state.process(agree)

    def skip(self):
        self.state.process('SKIP')

    def put(self, *args, **kw):
        def txn(key, *args, **kw):
            f = super(Round, self).put(*args, **kw)
            if key:
                game = db.get(key)
                game.close()
                game.put()
            return f

        key = self.winner and self.game.key() or None
        r = db.run_in_transaction(txn, key, *args, **kw)
        if r:
            if self.is_state(EndState):
                self.create_next()
        return r

    def clone(self):
        raise NotImplementedError('clone')

    def create_next(self):
        r = self.clone()
        r.turn += 1
        r.current_side = self.defence_side
        r.state = 'StartState'
        r.put()
        return r

    def prev(self):
        return self.game.rounds.filter('turn =',self.turn-1).get()

    def next(self):
        return self.game.rounds.filter('turn =',self.turn+1).get()

    def first(self):
        return self.game.rounds.filter('turn =',0).get()
        #return self.game.rounds.order('turn').get()

    def last(self):
        return self.game.rounds.order('-turn').get()

#    def state(self):
#        (self['state'] or NullState.new(self)).renew(self)
#
#    def state= state_class
#        old = self.state
#        new = state_class.new(self)
#
#        old.out_state_process(new)
#        self['state'] = new
#        new.in_state_process(old)
#
#        return self.state

    def _get_card_from_lines(self, card, player, troop_only=False):
        for line in player.lines:
            c = seq_finder(line.field, card.name, 'name')
            if c and troop_only and not c.is_troop:
                c = None
            if c:
                return [line.num, c]
        return [None, None]

    def restore_card(self, card):
        if card.is_troop:
            self.troops.insert(0, card)
        elif card.is_tactics:
            self.tactics.insert(0, card)

    def use_tactics(self):
        self.current_player.tactics_count += 1

    ############################
    # Numñ‚Ç¢çáÇÌÇπån

    @property
    def defence_side(self):
        return 1 - self.current_side

    def find_used_card(self, card):
        q = self.game.rounds.filter('turn <=',self.turn).order('-turn')
        seq = (x.process_get('PlayCardState')[0] for x in q)
        return seq_finder(seq, card)

    @property
    def my_player(self):
        #p = seq_finder(self.players, self.login_user(), 'user')
        for p in self.players:
            if p.user.user == users.get_current_user():
                return p
        raise RuntimeError('my player was not found')

    @property
    def opponent_player(self):
        #p = seq_finder(self.players, self.login_user(), 'user')
        for p in self.players:
            if p.user.user != users.get_current_user():
                return p
        raise RuntimeError('my player was not found')

    @property
    def winner(self):
        flags = self.flags
        def checker(lines):
            if len(lines) >= 3:
                for n in range(len(lines)-2):
                    if lines[n]+1 == lines[n+1] and \
                       lines[n+1] == lines[n+2]-1:
                        return True
            return False

        if len([p for p in flags if p==0]) >= 5:
            return 0
        elif len([p for p in flags if p==1]) >= 5:
            return 1
        elif checker([n for n in range(9) if flags[n] == 0]):
            return 0
        elif checker([n for n in range(9) if flags[n] == 1]):
            return 1
        else:
            return None

    ############################
    # boolñ‚Ç¢çáÇÌÇπån

    @property
    def is_my_side(self):
        return self.my_player.s_turn()

    def is_tactics_playable(self, player):
        counts = [x.tactics_count for x in self.players]
        diff = counts[0] - counts[1]
        if player.side == 1:
            diff *= -1
        return diff <= 0

    @property
    def is_card_stocks(self):
        return len(self.troops) > 0 or len(self.tactics) > 0

    @property
    def is_drowable(self):
        return self.is_troop_drowable or self.is_tactics_drowable

    @property
    def is_troop_drowable(self):
        if not (self.is_state(DrowState) or self.is_state(TacticsScoutDrowStateBase)):
            return False
        else:
            return len(self.troops) > 0

    @property
    def is_tactics_drowable(self):
        if not (self.is_state(DrowState) or self.is_state(TacticsScoutDrowStateBase)):
            return False
        else:
            return len(self.tactics) > 0

    def is_state(self, klass):
        if isinstance(klass, basestring):
            klass = globals()[klass]
        return isinstance(self.state, klass)

    def is_recent_used(self, card):
        if not card:
            return None

        try:
            if card == (self.process_get('PlayCardState')[0]): # rescue None):
                return True
            elif card == self.process_get(DrowState):
                return True
            elif card == (self.process_get(TacticsRedeployState)[0]): # rescue None):
                return True
            elif card == (self.process_get(TacticsTraitorState)[0]): # rescue None):
                return True
            elif card == self.process_get(TacticsDeserterState):
                return True
            elif card == self.process_get(TacticsScoutDrow1State):
                return True
            elif card == self.process_get(TacticsScoutDrow2State):
                return True
            elif card == self.process_get(TacticsScoutDrow3State):
                return True
            elif card == (self.process_get(TacticsScoutRestoreState)[0]): # rescue None):
                return True
            elif card == (self.process_get(TacticsScoutRestoreState)[1]): # rescue None):
                return True
        except:
            pass

        return False


    ############################
    # validation

#Player,Line ìôÇ≈çsÇ§Ç◊Ç´ÅB
#    def validate_line(num):
#        err = []
#        lines = self.lines[num]
#        weathers = lines['weathers']
#        fields = lines['fields']
#        for p, field in fields:
#            if len(field) > self.line_limit(num):
#                err.append("#{num}, over cards")
#
#            if any(c.is_weather for c in field) or any(c.is_plot for c in field):
#                err.append("#{num}, wrong assign")
#
#        for p, weth in weathers:
#            if not all(c.is_weather for c in weth):
#                err.append("#{num}, wrong assign")
#
#        return err
#
#    def validate_fields(self):
#        errors = []
#        for num in self.lines:
#            for e in self.validate_line(num):
#                #errors.add_to_base(e)
#                errors.append(e)


class RoundProcess(db.Model):
    round = db.ReferenceProperty(Round, required=True)
    state = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)


class Player(db.Model):
    _hand = db.ListProperty(db.Key, required=True) # card keys
    tactics_count = db.IntegerProperty(default=0, required=True)
    round = db.ReferenceProperty(Round, required=True)
    user = db.ReferenceProperty(GameUser, required=True)
    side = db.IntegerProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    # like named_scope
    lines = property(lambda s:s.line_set.order('num'))
    lines_s = lambda s,num:s.lines.filter('num =',num).get()

    # wrapper
    hand = ListPropertyAccessor('_hand')

    def name(self):
        # game.users[player-1].name rescue "Player#{player}" # ruby code
        return "Player%d" % self.side

    def s_turn(self):
        """ player.s_turn => True or False"""
        return self.key() == self.round.current_player.key()

    def is_playable(self):
        round = self.round
        if round.game.is_closed:
            return False
        elif not self.s_turn():
            return False
        elif not self.usable_cards():
            return False
        else:
            ## FIXME!! is_state is not working.
            return round.is_state(PlayCardState) or round.is_state(StartState)

    def is_hand_filled(self):
        return len(self.hand) >= 7

    def usable_cards(self):
        return [card for card in self.hand if card.is_usable(self)]
 
    def usable_lines(self):
        return [line for line in self.lines if line.is_usable()]


class Line(db.Model):
    _field = db.ListProperty(db.Key)
    _weather = db.ListProperty(db.Key)
    limit = db.IntegerProperty(default=3, required=True)
    is_proved = db.BooleanProperty(default=False, required=True)
    num = db.IntegerProperty(required=True)
    player = db.ReferenceProperty(Player)
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)

    # wrapper
    field = ListPropertyAccessor('_field')
    weather = ListPropertyAccessor('_weather')

    #def limit(self):
    #    #FIXME: MudCard class vs weather keys
    #    other = self.player.round.players.filter('side =', 1 - self.player.side).get().lines_s(self.num)
    #    if MudCard in self.weather or MudCard in other.weather:
    #        return 4
    #    return 3

    #def is_proved(self):
    #    return False
    #    #import time,sys
    #    #t = time.time()
    #    r = self.player.round.flags[self.num] != -1
    #    #t2 = time.time() - t
    #    #print >>sys.stderr, 'is_proved END', t2, 'sec'

    #    #print_stacktrace()
    #    return r

    def is_filled(self):
        return len(self.field) >= self.limit

    def is_usable(self):
        if self.is_proved:
            return False
        elif not self.is_filled():
            return True
        elif any(1 for x in self.player.hand if x.name=='Weather'):
            return True
        else:
            return False



def print_stacktrace():
    import sys,os
    f = sys._getframe(1)
    output = True
    while f:
        filename = f.f_code.co_filename
        funcname = f.f_code.co_name
        if output:
            print >>sys.stderr, """*** File "%s", line %s, in %s""" % (filename, f.f_lineno, funcname)
        if os.path.join('django','template','__init__.py') in filename:
            if funcname == 'resolve_variable':
                print >>sys.stderr, '   ### path=', f.f_locals.get('path')
            output = False
        if os.path.join('django','template','loader_tags.py') in filename:
            if funcname == 'render':
                s = f.f_locals.get('self')
                if s.template:
                    name = s.template.name
                else:
                    name = '<Unknown>'
                print >>sys.stderr, """*** File "%s", line %s, in %s""" % (filename, f.f_lineno, funcname)
                print >>sys.stderr, '   ### name=', name
        if os.path.join('controllers','controller_base.py') in filename:
            print >>sys.stderr, """*** File "%s", line %s, in %s""" % (filename, f.f_lineno, funcname)
            print >>sys.stderr, '   ### viewpath=', f.f_locals.get('viewpath')
            break
        f = f.f_back


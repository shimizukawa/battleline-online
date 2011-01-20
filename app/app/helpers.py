# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users
from app.models import Game, GameUser
import os
import time

from lib import template

from lib.utils import *


class Helper(object):

    def __init__(self, controller, context=None):
        self.controller = controller
        self.context = context

    def is_logged_in(self):
        return bool(self.login_user())

    def is_current_user_admin(self):
        return users.is_current_user_admin()

    #何に使うの？
    #def is_loginable(self):
    #    return User.count < 2 and self.is_logged_in()

    def login_user(self):
        return users.get_current_user()

    def login_name(self):
        u = self.login_user()
        return u and u.nickname() or u.email().split('@')[0]

    def login_url(self):
        return users.create_login_url(self.controller.request.uri)

    def logout_url(self):
        return users.create_logout_url(self.controller.request.uri)

    def progress_time(self, game):
        if game.rounds.count() == 0:
            return '0:00:00'
        secs = time.time() - time.mktime(game.rounds[0].created_at.timetuple())
        h = secs / 3600
        m = secs / 60 % 60
        s = secs % 60
        return ':'.join(['%02d' % d for d in [h,m,s]])

    #ログインだけのユーザーは見ない事にした。
    #ゲームしているユーザー一覧に移行
    def login_users(self):
        raise DeprecationWarning('login_users')
        #return User.all().filter('state=','LOGIN')

    def playing_users(self):
        return GameUser.playing_users()
        #return GameUser.all().filter('game.state=OPEN')

    def gamelist(self):
        return Game.active()
        #return Game.all().filter('state !=', 'CLOSED')


###############
# Play

    def render_card(self, card, front=True, index=None):
        apppath = self.controller._app_path
        name = self.controller._controller_name
        filename = '_card.html'
        viewpath = os.path.join(apppath, 'views', name, filename)
        values = {'helper': self, 'front': front,}
        if index is None or card is None:
            values['card'] = card
        else:
            values['card'] = card[index]
        return template.render(viewpath, values)

    def submit_tag2(self, value, **attrs):
        #tag = submit_tag(*args) # ruby code...
        opt = ' '.join('%s="%s"' % item for item in attrs.items())
        tag = '<input type="submit" value="%s" %s>' % (value, opt)
        if 'disabled' in tag:
            return tag
        else:
            return '<span class="button-highlight">%s</span>' % tag

    def field_tag(self, rowtype, rowid, player):
        ROW_TYPES = {
            0: 'field',
            1: 'weather',
        }
        rowtype = ROW_TYPES[rowtype]
        round = self.context.get('round')
        if not player:
            return '<td></td>' * 9

        results = []
        for line in player.lines:
            flag = round.flags[line.num]
            cls = []
            if flag >= 0:
                cls.append("player-%d" % flag)
            try:
                card = getattr(line, rowtype)[rowid]
            except IndexError,e:
                card = None
            results.append('<td class="%s">%s</td>' % (
                           ' '.join(cls),
                           self.render_card(card)
            ))
        return ''.join(results)

    def field_flag_tag(self, player=None):
        round = self.context.get('round')
        results = []
        for n,flag in enumerate(round.flags):
            cls = ['flagline']
            if player is None:
                f = (flag == -1) and u'●' or ''
                f = "%d%s" % (n+1, f)
                cls.append('centerline')
            else:
                f = (flag == player.side) and u'●' or ''
            if flag >= 0:
                cls.append("player-%d" % flag)
            results.append('<td class="%s"><span>%s</span></td>' % (
                          ' '.join(cls), f))
        return ''.join(results)

    def field_select_tag(self, player):
        lines = []
        for line in player.lines:
            if player.is_playable and line.is_usable():
                l = '<input type="radio" name="selectline" value="%d">' % line.num
            else:
                l = ''
            lines.append(l)

        return ''.join('<td class="noborder">%s</td>' % x for x in lines)



#   def is_troop_drowable
#     if @round.my_player.side == @round.current_side
#       @round.is_troop_drowable
#     else
#       false
#     end
#   end
# 
#   def is_tactics_drowable
#     if @round.my_player.side == @round.current_side
#       @round.is_tactics_drowable
#     else
#       false
#     end
#   end

 
#   def is_need_to_setup_tactics
#     if @round.my_player.side != @round.current_side
#       false
#     elsif @round.is_state TacticsScoutDrowStateBase
#       false
#     else
#       @round.is_state TacticsStateBase
#     end
#   end
 
    def is_can_skip(self):
        round = self.context.get('round')
        if not round.is_my_side:
            return False
        elif not(round.is_state('PlayCardState') or round.is_state('StartState')):
            return False
        elif not round.my_player.usable_lines():
            return True

    def is_provable(self):
        round = self.context.get('round')
        if not round.is_my_side:
            return False
        elif round.is_state('StartState'):
            return True
        else:
            return False

#   def is_need_to_proof
#     if not @round.is_my_side
#       false
#     elsif @round.state? ProofSelectState
#       true
#     else
#       false
#     end
#   end

    def is_need_to_judge(self):
        round = self.context.get('round')
        if round.is_my_side:
            return False
        elif round.is_state('ProofJudgeState'):
            return True
        else:
            return False

#   def proving_line
#     @round.process[ProofSelectState.to_s.to_sym]
#   end
# 

    @property
    def provable_lines(self):
        round = self.context.get('round')
        return [i for i,x in enumerate(round.flags) if x != -1]

    def recent_play_style(self, card):
        round = self.context.get('round')
        return ''
        # rounds = [@round, @round.prev, (@round.prev.prev rescue nil)].find_all{|r|r.process[:PlayCardState] rescue false}
        # rounds[0..1].each do |round|
        #   if round.is_recent_used card
        #     return "card-recent-play player-#{round.current_side}"
        #   end
        # end

#   def card_view round, card
#     render_card card, round.is_my_side
#   end
# 
#   def deserter_target_cards
#     side = @round.defence_side
#     cards = []
#     @round.lines.each do |l,line|
#       flag = line[:flag]
#       line[:fields][side].each do |card|
#         cards << card unless flag
#       end
#     end
#     cards.sort
#   end
# 
#   def traitor_target_cards
#     side = @round.defence_side
#     cards = []
#     @round.lines.each do |l,line|
#       flag = line[:flag]
#       line[:fields][side].each do |card|
#         cards << card if flag==nil && card.is_troop
#       end
#     end
#     cards.sort
#   end
# 
#   def redeploy_target_cards
#     side = @round.current_side
#     cards = []
#     @round.lines.each do |l,line|
#       flag = line[:flag]
#       line[:fields][side].each do |card|
#         cards << card unless flag
#       end
#     end
#     cards.sort
#   end
# 
#   def rounds_for_display_process(count)
#     rounds = []
#     r = @round
#     while r && rounds.size < count
#       if r.process.size > 0
#         rounds << r
#       end
#       r = r.prev
#     end
#     rounds
#   end


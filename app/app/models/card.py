# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import re


__all__ = [
    'Card',
    'TroopCard', 'TacticsCard',
    'SpiritCard', 'PlotCard', 'WeatherCard',

    'AlexanderCard', 'DariusCard', 'CompanionCard', 'ShieldCard',

    'FogCard', 'MudCard', 'ScoutCard',
    'RedeployCard', 'DeserterCard', 'TraitorCard',
]

 
SPIRIT_CARDS = ['ALEXANDER', 'DARIUS', 'COMPANION', 'SHIELD']
WEATHER_CARDS = ['FOG', 'MUD']
PLOT_CARDS = ['SCOUT', 'REDEPLOY', 'DESERTER', 'TRAITOR']
TACTICS_CARDS = (SPIRIT_CARDS + WEATHER_CARDS + PLOT_CARDS)


class Card(polymodel.PolyModel):
    name = db.StringProperty()

    @staticmethod
    def create_troops():
        q = TroopCard.all()
        if q.count() == 0:
            r = [Card.new_by_name('%s%d' % (c, n))
                 for c in 'ABCDEF'
                 for n in range(1,11)]
        else:
            r = [x for x in q]
        return r

    @staticmethod
    def create_tactics():
        q = TacticsCard.all()
        if q.count() == 0:
            r = [Card.new_by_name(name) for name in TACTICS_CARDS]
        else:
            r = [x for x in q]
        return r

    @staticmethod
    def new_by_name(name):
        if name in TACTICS_CARDS:
            card = TACTICS_CARD_CLASSES[name]()
        else:
            card = TroopCard(name=name)
        card.put()
        return card

    @property
    def is_troop(self):
        return not self.is_tactics

    @property
    def is_tactics(self):
        return self.name in TACTICS_CARDS

    @property
    def is_spirit(self):
        return self.name in SPIRIT_CARDS

    @property
    def is_weather(self):
        return self.name in WEATHER_CARDS

    @property
    def is_plot(self):
        return self.name in PLOT_CARDS

    @property
    def is_play_tactics(self):
        return self.is_spirit or self.is_plot

    def is_usable(self, player):
        round = player.round
        if self.is_troop:
            return len(player.usable_lines()) > 0
        elif not round.is_tactics_playable(player):
            return False
        elif self.is_spirit and len(player.usable_lines()) == 0:
            return False
        elif self.name == 'Alexander':
            r = round.find_used_card('Darius')
            return not (r and r.current_side == player.side)
        elif self.name == 'Darius':
            r = round.find_used_card('Alexander')
            return not (r and r.current_side == player.side)
        else:
            return True

#    def == other:
#        (self <=> other) == 0
#        rescue
#            false
#        end
#    end

class TroopCard(Card):

    def __str__(self):
        return '%s%d' % (self.color, self.number)

    @property
    def color(self):
        return re.match('([A-F])(\d{1,2})', self.name).group(1)

    @property
    def number(self):
        return int(re.match('([A-F])(\d{1,2})', self.name).group(2))

    def __cmp__(self, other):
        if other.is_troop:
            v = cmp(self.color, other.color)
            if v == 0:
                return cmp(self.number, other.number)
            else:
                return v
        else:
            return -1


class TacticsCard(Card):
    pass


class SpiritCard(TacticsCard):
    role = db.ReferenceProperty(TroopCard)

    def __str__(self):
        label = self.name
        label += self.role and ("(%s)" % self.role) or ''
        return label

    def __cmp__(self, other):
        if other.is_troop:
            return 1
        elif other.is_spirit:
            return cmp(self.name, other.name)
        else:
            return -1


class AlexanderCard(SpiritCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'ALEXANDER'
        super(AlexanderCard, self).__init__(*args, **kw)


class DariusCard(SpiritCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'DARIUS'
        super(DariusCard, self).__init__(*args, **kw)


class CompanionCard(SpiritCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'COMPANION'
        super(CompanionCard, self).__init__(*args, **kw)

#    def validate(self):
#        raise "invalid card role #{card}" unless card.number == 8


class ShieldCard(SpiritCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'SHIELD'
        super(ShieldCard, self).__init__(*args, **kw)

#    def validate(self):
#        raise 'invalid card role' unless (1..3).include? card.number


class WeatherCard(TacticsCard):
    def __cmp__(self, other):
        if other.is_plot:
            return -1
        elif other.is_weather:
            return cmp(self.name, other.name)
        else:
            return 1


class FogCard(WeatherCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'FOG'
        super(FogCard, self).__init__(*args, **kw)


class MudCard(WeatherCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'MUD'
        super(MudCard, self).__init__(*args, **kw)


class PlotCard(TacticsCard):
    def __cmp__(self, other):
        if other.is_plot:
            return cmp(self.name, other.name)
        else:
            return 1


class ScoutCard(PlotCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'SCOUT'
        super(ScoutCard, self).__init__(*args, **kw)


class RedeployCard(PlotCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'REDEPLOY'
        super(RedeployCard, self).__init__(*args, **kw)


class DeserterCard(PlotCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'DESERTER'
        super(DeserterCard, self).__init__(*args, **kw)


class TraitorCard(PlotCard):
    def __init__(self, *args, **kw):
        kw['name'] = 'TRAITOR'
        super(TraitorCard, self).__init__(*args, **kw)


TACTICS_CARD_CLASSES = {
    'ALEXANDER': AlexanderCard,
    'DARIUS': DariusCard,
    'COMPANION': CompanionCard,
    'SHIELD': ShieldCard,
    'FOG': FogCard,
    'MUD': MudCard,
    'SCOUT': ScoutCard,
    'REDEPLOY': RedeployCard,
    'DESERTER': DeserterCard,
    'TRAITOR': TraitorCard,
}

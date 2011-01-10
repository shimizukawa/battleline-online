# -*- coding: utf-8 -*-

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


class Card(object):
    name = ''

    @staticmethod
    def new_by_name(name):
        if name in TACTICS_CARDS:
            card = TACTICS_CARD_CLASSES[name]()
        else:
            card = TroopCard(name=name)
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

    def __init__(self, name):
        self.name = name

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
    role = ''

    def __str__(self):
        return self.name

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

def create_troops():
    return [Card.new_by_name('%s%d' % (c, n))
            for c in 'ABCDEF'
            for n in range(1,11)]

def create_tactics():
    return [Card.new_by_name(name) for name in TACTICS_CARDS]


TROOPS = create_troops()
TACTICS = create_tactics()

CARD_DICT = dict([(c.name, c) for c in TROOPS])
CARD_DICT.update(dict([(c.name, c) for c in TACTICS]))






#=======================================================================


class CardList(object):
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.cards = getattr(parent, name)

    def __getitem__(self, index):
        return CARD_DICT[self.cards[index]]

    def __setitem__(self, index, obj):
        getattr(self.__parent__, self.__name__)[index] = obj.name
        self.cards[index] = obj.name

    def __iter__(self):
        return (CARD_DICT[name] for name in getattr(self.__parent__, self.__name__))

    def __len__(self):
        return len(self.cards)

    @property
    def size(self):
        """ compatible to db.ListProperty query object attribute """
        return len(self)

    def pop(self, index):
        return CARD_DICT[self.cards.pop(index)]

    def append(self, obj):
        return self.cards.append(obj.name)

    def remove(self, obj):
        return self.cards.remove(obj.name)

    def insert(self, index, obj):
        return self.cards.insert(index, obj.name)


class CardListProperty(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, klass):
        return CardList(instance, self.name)

    def __set__(self, instance, value):
        setattr(instance, self.name, [obj.name for obj in value])


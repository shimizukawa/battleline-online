# -*- coding: utf-8 -*-

from lib.utils import *

__all__ = [
    'StateBase', 'NullState', 'StartState',
    'DrowState', 'EndState', 'PlayCardState',
    'ProofJudgeState', 'ProofSelectState', 'ProofStateBase',
    'TacticsDeserterState', 'TacticsRedeployState',
    'TacticsScoutDrow1State', 'TacticsScoutDrow2State',
    'TacticsScoutDrow3State', 'TacticsScoutDrowStateBase',
    'TacticsScoutRestore1State', 'TacticsScoutRestore2State',
    'TacticsScoutRestoreStateBase', 'TacticsScoutStateBase',
    'TacticsSpiritState', 'TacticsStateBase',
    'TacticsTraitorState', 'TacticsWeatherState',
]



class StateBase(object):
#    def to_yaml_properties(self):
#        instance_variables.find_all{|name|name!='self.round'}.sort
#    end

    @classmethod
    def instance(cls, klass, round):
        if isinstance(klass, basestring):
            if klass in globals():
                klass = globals()[klass]
            else:
                klass = NullState
        elif isinstance(klass, StateBase):
            pass
        else:
            raise ValueError('%r must basestring or StateBase delivered class')
        return klass(round)

    def __init__(self, round):
        self.round = round

    def renew(self, round):
        self.round = round
        return self

    def __str__(self):
        return self.__class__.__name__

    @apply
    def result():
        def getter(self, state=None):
            """ 同一Round内での特定のStateでの結果を取得"""
            # state must be Class
            cls = state and state or self
            return self.round.process[cls.__class__.__name__]

        def setter(self, obj):
            """ 現在のStateでの結果を登録し、stateを次に進める"""
            self.round.process[str(self)] = obj
            #self.round.process_will_change!
            self.round.state = self.nextstate
            return self.nextstate

        return property(getter, setter)

    # stateに入った時に実行される処理
    def in_state_process(self, prev_state):
        pass

    # 現在のstateでの主処理
    def process(self, *args):
        raise NotImplementedError()

    # stateを出る時に実行される処理
    def out_state_process(self, next_state):
        pass

    # 次のstateを取得
    def nextstate(self):
        raise NotImplementedError()


class NullState(StateBase):
    pass


class StartState(StateBase):
    def process(self, *args):
        if isinstance(args[0], Card):
            self.round.state = PlayCardState
            self.round.state.process(*args)
        elif args[0] == "PROOF":
            self.round.state = ProofSelectState
            self.round.state.process(*args)
        elif args[0] == "SKIP":
            self.round.state = DrowState
        else:
            raise RuntimeError("Ambiguous State processing")

    def nextstate(self):
        pass


class PlayCardState(StateBase):
    def process(self, card, line=None):
        side = self.round.current_side
        player = self.round.current_player
        #logger.debug("side: #{side}")
        #logger.debug('hand: ' + self.round.hands[side].join(','))

        # check
        card = seq_finder(player.hand, card.name, 'name')
        if card is None:
            raise RuntimeError("Invalid Card Select")

        # update
        if card.is_troop or card.is_spirit:
            player.lines_s(line).field.append(card)
        elif card.is_weather:
            player.lines_s(line).weather.append(card)
        elif card.is_plot:
            self.round.discards.append(card)
        else:
            raise RuntimeError("Unknown Card")

        player.hand.remove(card)
        self.result = [card, line]

    def nextstate(self):
        card = self.result[0]
        if card.is_spirit:
            return TacticsSpiritState
        elif card.is_weather:
            return TacticsWeatherState
        elif card.is_plot:
            results = {
                'DESERTER': TacticsDeserterState,
                'TRAITOR': TacticsTraitorState,
                'REDEPLOY': TacticsRedeployState,
                'SCOUT': TacticsScoutDrow1State,
            }
            if card.name not in results:
                raise RuntimeError("Unknown card")
            return results[card.name]
        else:
            return DrowState


class DrowState(StateBase):
    def in_state_process(self, prev_state):
        if not self.round.is_card_stocks:
            self.result = None
        elif self.round.current_player.is_hand_filled():
            self.result = None

    def process(self, cardtype):
        if cardtype == 'TROOP':
            card = self.drow_troop()
        elif cardtype == 'TACTICS':
            card = self.drow_tactics()
        self.round.sort_hands()
        self.round.hands[self.round.current_side].append(card)
        #self.round.hands_will_change!
        self.result = card
        return card

    def drow_troop(self):
        if self.round.troops.size == 0:
            raise RuntimeError("no troops")
        #self.round.troops_will_change!
        return self.round.troops.pop(0)

    def drow_tactics(self):
        if self.round.tactics.size == 0:
            raise RuntimeError("no tactics")
        #self.round.tactics_will_change!
        return self.round.tactics.pop(0)

    def nextstate(self):
        return EndState


class TacticsStateBase(StateBase):
    def nextstate(self):
        return DrowState


class TacticsSpiritState(TacticsStateBase):
    def in_state_process(self, prev_state):
        # skip state
        pc, pl = self.result(PlayCardState)
        self.round.use_tactics()
        self.result = pc


class TacticsWeatherState(TacticsStateBase):
    def in_state_process(self, prev_state):
        # skip state
        pc, pl = self.result(PlayCardState)
        self.round.use_tactics()
        self.result = pc


class TacticsDeserterState(TacticsStateBase):
    def process(self, card, to):
        # 相手フィールドからTROOPかSPIRITを1枚破棄
        pc, pl = self.result(PlayCardState)
        player = self.round.defence_player
        ln, card = self.round._get_card_from_lines(card, player)
        if not ln:
            raise RuntimeError("wrong card")
        player.lines_s(ln).field.remove(card)
        self.round.discards.append(card)
        self.round.use_tactics()
        #logger.debug(card.inspect)
        #logger.debug(player.lines_s(ln).field.inspect)
        self.result = card


class TacticsTraitorState(TacticsStateBase):
    def process(self, card, to):
        # 相手フィールドからTROOPを1枚自分のフィールドへ再配置
        pc, pl = self.result(PlayCardState)
        #logger.debug(card.inspect)
        #logger.debug(to.inspect)
        defence_player = self.round.defence_player
        ln, card = self.round._get_card_from_lines(card, defence_player, True)
        if not ln:
            raise RuntimeError("wrong card")
        if to not in range(9):
            raise RuntimeError("wrong line")

        defence_player.lines_s(ln).field.remove(card)
        self.round.current_player.lines_s(to).field.append(card)
        self.round.use_tactics()
        self.result = [card, to]


class TacticsRedeployState(TacticsStateBase):
    def process(self, card, to):
        # 自分のフィールドからTROOPかSPIRITを1枚再配置、または破棄
        pc, pl = self.result(PlayCardState)
        #logger.debug(card.inspect)
        #logger.debug(to.inspect)
        player = self.round.current_player
        ln, card = self.round._get_card_from_lines(card, player)
        if not ln:
            raise RuntimeError("wrong card")
        if not to:
            raise RuntimeError("wrong line")

        player.lines_s(ln).field.remove(card)
        if to in range(9):
            player.lines_s(to).field.append(card)
        elif to == 'discard':
            self.round.discards.append(card)
        self.round.use_tactics()
        self.result = [card, to]


class TacticsScoutStateBase(TacticsStateBase):
    # 3枚を任意の山から引き、2枚を戻す
    pass

class TacticsScoutDrowStateBase(TacticsScoutStateBase):
    def process(self, cardtype):
        # 3枚を任意の山から引き、2枚を戻す
        if cardtype == 'TROOP':
            card = self.drow_troop()
        elif cardtype == 'TACTICS':
            card = self.drow_tactics()
        player = self.round.current_player
        player.hand.append(card)
        self.result = card

    def drow_troop(self):
        if not self.round.troops:
            raise RuntimeError("no troops")
        return self.round.troops.pop(0)

    def drow_tactics(self):
        if not self.round.tactics:
            raise RuntimeError("no tactics")
        return self.round.tactics.pop(0)


class TacticsScoutDrow1State(TacticsScoutDrowStateBase):
    # 1枚目
    def nextstate(self):
        return TacticsScoutDrow2State


class TacticsScoutDrow2State(TacticsScoutDrowStateBase):
    # 2枚目
    def nextstate(self):
        return TacticsScoutDrow3State


class TacticsScoutDrow3State(TacticsScoutDrowStateBase):
    # 3枚目
    def nextstate(self):
        return TacticsScoutRestore1State


class TacticsScoutRestoreStateBase(TacticsScoutStateBase):
    def process(self, card, *args):
        if not card:
            raise RuntimeError("wrong card")
        player = self.round.current_player
        card = seq_finder(player.hand, card)
        if not card:
            raise RuntimeError("wrong card")
        player.hand.remove(card)
        self.round.restore_card(card)
        self.result = card


class TacticsScoutRestore1State(TacticsScoutRestoreStateBase):
    # 1枚目
    def nextstate(self):
        return TacticsScoutRestore2State


class TacticsScoutRestore2State(TacticsScoutRestoreStateBase):
    # 2枚目
    def out_state_process(self, next_state):
        self.round.use_tactics()

    def nextstate(self):
        return EndState


class ProofStateBase(StateBase):
    pass

class ProofSelectState(ProofStateBase):
    def process(self, marker, line=None):
        if marker == 'PROOF':
            if not line:
                raise RuntimeError("line must be selected.")
            if self.round.flag[line]:
                line = None
            self.result = line
        elif marker == 'CANCEL':
            self.result = None

    def nextstate(self):
        if self.result:
            return ProofJudgeState
        else:
            return StartState


class ProofJudgeState(ProofStateBase):
    def process(self, agree):
        line = self.result(ProofSelectState)
        if agree:
            self.round.flag[line] = self.round.current_side
        self.result = [line, agree]

    def nextstate(self):
        return StartState


class EndState(StateBase):
    def in_state_process(self, prev_state):
        if not self.result(EndState):
            self.result = True

    def nextstate(self):
        return self.__class__
 
 

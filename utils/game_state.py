from enum import Enum, unique
import copy

""" Example round state generated by emulator

        {'street': 'river', 'pot': {'main': {'amount': 400}, 'side': []},
         'community_card': ['DT', 'C2', 'ST', 'DA', 'HT'],
         'dealer_btn': 1, 'next_player': 1, 'small_blind_pos': 0, 'big_blind_pos': 1, 'round_count': 10,
         'small_blind_amount': 10,
         'seats': [{'name': 'f1', 'uuid': 'zdmxlmfwytkigodciubiow', 'stack': 10200, 'state': 'participating'},
                   {'name': 'FT2', 'uuid': 'lnjvmobrxhizukrppiqbda', 'stack': 9400, 'state': 'participating'}],
         'action_histories': {
             'preflop': [{'action': 'SMALLBLIND', 'amount': 10, 'add_amount': 10, 'uuid': 'zdmxlmfwytkigodciubiow'},
                         {'action': 'BIGBLIND', 'amount': 20, 'add_amount': 10, 'uuid': 'lnjvmobrxhizukrppiqbda'},
                         {'action': 'RAISE', 'amount': 40, 'paid': 30, 'add_amount': 20,
                          'uuid': 'zdmxlmfwytkigodciubiow'},
                         {'action': 'RAISE', 'amount': 60, 'paid': 40, 'add_amount': 20,
                          'uuid': 'lnjvmobrxhizukrppiqbda'},
                         {'action': 'RAISE', 'amount': 80, 'paid': 40, 'add_amount': 20,
                          'uuid': 'zdmxlmfwytkigodciubiow'},
                         {'action': 'CALL', 'amount': 80, 'paid': 20, 'uuid': 'lnjvmobrxhizukrppiqbda'}],
             'flop': [{'action': 'RAISE', 'amount': 20, 'paid': 20, 'add_amount': 20, 'uuid': 'zdmxlmfwytkigodciubiow'},
                      {'action': 'RAISE', 'amount': 40, 'paid': 40, 'add_amount': 20, 'uuid': 'lnjvmobrxhizukrppiqbda'},
                      {'action': 'RAISE', 'amount': 60, 'paid': 40, 'add_amount': 20, 'uuid': 'zdmxlmfwytkigodciubiow'},
                      {'action': 'RAISE', 'amount': 80, 'paid': 40, 'add_amount': 20, 'uuid': 'lnjvmobrxhizukrppiqbda'},
                      {'action': 'CALL', 'amount': 80, 'paid': 20, 'uuid': 'zdmxlmfwytkigodciubiow'}],
             'turn': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'zdmxlmfwytkigodciubiow'},
                      {'action': 'RAISE', 'amount': 40, 'paid': 40, 'add_amount': 40, 'uuid': 'lnjvmobrxhizukrppiqbda'},
                      {'action': 'CALL', 'amount': 40, 'paid': 40, 'uuid': 'zdmxlmfwytkigodciubiow'}],
             'river': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'zdmxlmfwytkigodciubiow'}]}}
"""


# TODO: check if showdown is a street
# TODO: use property getter/setter where applicable
class State:

    def __init__(self, round_state, hole_card, is_terminal=False):
        self._round_state = round_state
        self.p0_uuid = round_state['seats'][0]['uuid']
        self.p1_uuid = round_state['seats'][1]['uuid']
        self.p0_raises = 0
        self.p1_raises = 0
        self.preflop_raises = 0
        self.flop_raises = 0
        self.turn_raises = 0
        self.river_raises = 0
        self.curr_street_raises = 0
        self.prev_history = ''
        self.street = self._round_state['street']
        self.known_card = []

        for street, street_history in round_state['action_histories'].items():
            """
            In Python 3.7.0 the insertion-order preservation nature of dict objects has been declared to be an 
            official part of the Python language spec. Therefore, you can depend on it"
            """
            self.curr_street_raises = 0
            for ply in street_history:
                if ply['action'] == 'RAISE':
                    # Add raises to appropriate street
                    if street == 'preflop':
                        self.preflop_raises += 1
                    elif street == 'flop':
                        self.flop_raises += 1
                    elif street == 'turn':
                        self.turn_raises += 1
                    else:  # last street is river
                        self.river_raises += 1

                    # Add raises to appropriate player
                    if ply['uuid'] == self.p0_uuid:
                        self.p0_raises += 1
                    else:
                        self.p1_raises += 1

                    # Increment current street raises
                    self.curr_street_raises += 1

                self.prev_history = ply

        for card in hole_card:
            self.known_card.append(convert_card_to_index(card))

        for card in self._round_state['community_card']:
            self.known_card.append(convert_card_to_index(card))

        self.current_player = round_state['next_player']
        self.p0_stack = round_state['seats'][0]['stack']

        self.p1_stack = round_state['seats'][1]['stack']
        self.is_terminal = is_terminal

    def current_player_uuid(self):
        return self.p0_uuid if self.current_player == 0 else self.p1_uuid

    def raise_bet(self):
        new_round_state = copy.deepcopy(self._round_state)
        new_add_amount = 20 if self._round_state['street'] in ['preflop', 'flop'] else 40
        new_amount = self.prev_history['amount'] + new_add_amount
        # Note, the below does not lend compatibility to the preflop street
        new_paid = 2 * new_add_amount if self.prev_history['action'] == 'RAISE' else new_add_amount

        new_round_state['pot']['main']['amount'] += new_add_amount
        new_round_state['next_player'] += 1
        new_round_state['next_player'] %= 2
        new_round_state['seats'][self.current_player]['stack'] -= new_add_amount
        new_round_state_action_histories = new_round_state['action_histories']
        if self.street in new_round_state_action_histories:
            new_round_state_action_histories[self.street].append({
                'action': 'RAISE',
                'amount': new_amount,
                'paid': new_paid,
                'add_amount': new_add_amount,
                'uuid': self.current_player_uuid()
            })
        else:
            new_round_state_action_histories[self.street] = [{
                'action': 'RAISE',
                'amount': new_amount,
                'paid': new_paid,
                'add_amount': new_add_amount,
                'uuid': self.current_player_uuid()
            }]

        return State(new_round_state)

    def fold_bet(self):
        new_round_state = copy.deepcopy(self._round_state)
        new_round_state_action_histories = new_round_state['action_histories']
        if self.street in new_round_state_action_histories:
            new_round_state_action_histories[self.street].append({
                'action': 'FOLD',
                'uuid': self.current_player_uuid()
            })
        else:
            new_round_state_action_histories[self.street] = [{
                'action': 'FOLD',
                'uuid': self.current_player_uuid()
            }]

        return State(new_round_state, True)

    def call_bet(self):
        raise NotImplementedError

    def switch_player(self):
        self.current_player += 1
        self.current_player %= 2

    def add_one_more_community_card(self, card):
        if self.street == 'flop':
            self.street = 'turn'
        elif self.street == 'turn':
            self.street = 'river'
        self.community_card.append(card)
        self.switch_player()


# TODO: Replace poker game actions with Enums.
@unique
class Action(Enum):
    FOLD = 0
    CALL = 1
    RAISE = 2


class PokerGame:  # Static util class for State 

    def __init__(self, current_state=None, search_algorithm=None, evaluation_function=None):
        pass

    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        if self.terminal_test(state):
            return []

        can_raise = state.curr_street_raises < 4 and \
                          (state.p0_raises < 4 if state.current_player == 0 else state.p1_raises < 4)

        if can_raise:
            return ['FOLD', 'CALL', 'RAISE']
        else:
            return ['FOLD', 'CALL']

    def result(self, state, action):
        """Return the state that results from making a move from a state."""
        state.switch_player()
        return {'FOLD': state.fold_bet,
                'RAISE': state.raise_bet,
                'CALL': state.call_bet}[action]()

    # TODO: our agent may not always be player 0
    def utility(self, state, player):
        if state.prev_history['action'] == 'FOLD':
            if player == state._round_state['next_player']:  # When folding, the next player remains as the player who folded
                return - state._round_state['pot']['main']
            else:
                return state._round_state['pot']['main']

        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return state.is_terminal

    def convert_card_to_index(self, card):
        chars = list(card)
        suite = {
            'C': 0,
            'D': 13,
            'H': 26,
            'S': 39}
        rank = {
            '2': 0,
            '3': 1,
            '4': 2,
            '5': 3,
            '6': 4,
            '7': 5,
            '8': 6,
            '9': 7,
            'T': 8,
            'J': 9,
            'Q': 10,
            'K': 11,
            'A': 12}
        return suite[chars[0]] + rank[chars[1]]

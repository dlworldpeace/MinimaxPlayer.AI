import copy
from enum import Enum, unique
import pprint
from pypokerengine.utils.card_utils import (estimate_hole_card_win_rate,
                                            gen_cards)


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
             'river': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'zdmxlmfwytkigodciubiow'}]}
            
             }
"""


""" Example new_round_state modified by state class

        {
         'street': 'river', 'pot': {'main': {'amount': 400}, 'side': []},
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
             'river': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'zdmxlmfwytkigodciubiow'}]}

         'preflop_raises' : 2,
         'flop_raises' : 3,
         'turn_raises' : 2,
         'river_raises' : 2,
         'p0_raises' : 4,
         'p1_raises' : 5,
         'current_street_raises' : { 'river' : 2},
         'prev_history' : {'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'zdmxlmfwytkigodciubiow'},
         'p0_prev_amount' : 40,
         'p1_prev_amount' : 20
        }
"""

# TODO: check if showdown is a street
# TODO: use property getter/setter where applicable
class State:

    def __init__(self, round_state, hole_card_indices, community_card_indices, is_cached = False, is_terminal = False):
        self._round_state = round_state
        self.p0_uuid = round_state['seats'][0]['uuid']
        self.p1_uuid = round_state['seats'][1]['uuid']
        self.street = self._round_state['street']
        self.prev_history = ''
        self.is_cached = is_cached
        self.new_round_state = copy.deepcopy(self._round_state)
        self.hole_card_indices = hole_card_indices
        self.community_card_indices = community_card_indices


        if not is_cached : 
            self.new_round_state['preflop_raises'] = 0
            self.new_round_state['flop_raises'] = 0
            self.new_round_state['turn_raises'] = 0
            self.new_round_state['river_raises'] = 0
            self.new_round_state['p0_raises'] = 0
            self.new_round_state['p1_raises'] = 0
            self.new_round_state['current_street_raises'] = {}
            self.new_round_state['prev_history'] = {}
            self.new_round_state['p0_prev_amount'] = 0
            self.new_round_state['p1_prev_amount'] = 0
            eventsorder= ['preflop', 'flop', 'turn', 'river','showdown']
            for street, street_history in sorted(round_state['action_histories'].items(), key = lambda i : eventsorder.index(i[0])):
                """
                In Python 3.7.0 the insertion-order preservation nature of dict objects has been declared to be an 
                official part of the Python language spec. Therefore, you can depend on it"
                """

                for ply in street_history:
                    if ply['action'] == 'RAISE':
                        # Add raises to appropriate street
                        if street == 'preflop':
                            if 'preflop_raises' in self.new_round_state :
                                self.new_round_state['preflop_raises'] += 1
                            else :    
                                self.new_round_state['preflop_raises'] = 1
                        elif street == 'flop':
                            if 'flop_raises' in self.new_round_state :
                                self.new_round_state['flop_raises'] += 1
                            else :    
                                self.new_round_state['flop_raises'] = 1
                        elif street == 'turn':
                            if 'turn_raises' in self.new_round_state :
                                self.new_round_state['turn_raises'] += 1
                            else :    
                                self.new_round_state['turn_raises'] = 1
                        else:  # last street is river
                            if 'river_raises' in self.new_round_state :
                                self.new_round_state['river_raises'] += 1
                            else :    
                                self.new_round_state['river_raises'] = 1
    
                        # Add raises to appropriate player
                        if ply['uuid'] == self.p0_uuid:
                            if 'p0_raises' in self.new_round_state :
                                self.new_round_state['p0_raises'] += 1
                            else :    
                                self.new_round_state['p0_raises'] = 1
                            
                            # Add latest amount of p0 to p0_prev_amount
                            self.new_round_state['p0_prev_amount'] = ply['amount']

                        else:
                            if 'p1_raises' in self.new_round_state :
                                self.new_round_state['p1_raises'] += 1
                            else :    
                                self.new_round_state['p1_raises'] = 1

                            # Add latest amount of p1 to p1_prev_amount
                            self.new_round_state['p1_prev_amount'] = ply['amount']

                        # Increment current street raises
                        # If street is not in current_street_raises attribute, it means that the street has changed and must changed curr_street_raises accordingly
                        if 'current_street_raises' in self._round_state :
                            if street not in self._round_state['current_street_raises'] :
                                self.new_round_state['current_street_raises'] = {street : 1}
                            else :
                                self.new_round_state['current_street_raises'][street] += 1
                        else :
                            self.new_round_state['current_street_raises'] = {street : 1}
       

                    self.new_round_state['prev_history'] = ply
                    # Add prev_history to attribute if it has not been cached before
                    self.prev_history = ply
            self.is_cached = True       

        else :
            # It has been cached before, so the attribute should be in the round state
            self.prev_history = self._round_state['prev_history']

        self.current_player = self._round_state['next_player']
        self.p0_stack = self._round_state['seats'][0]['stack']
        self.p1_stack = round_state['seats'][1]['stack']
        self.is_terminal = is_terminal

    def get_new_round_state(self) :
        return self.new_round_state

    def get_preflop_raises (self) :
        return self.new_round_state['preflop_raises']

    def get_flop_raises (self) :
        return self.new_round_state['flop_raises']

    def get_turn_raises (self) :
        return self.new_round_state['turn_raises']

    def get_river_raises (self) :
        return self.new_round_state['river_raises']    

    def get_p0_raises (self) :
        return self.new_round_state['p0_raises']

    def get_p1_raises (self) :
        return self.new_round_state['p1_raises']   

    def get_current_street_raises (self) :
        return self.new_round_state['current_street_raises'][self.street]   

    def get_prev_history (self) :
        return self.new_round_state['prev_history']   

    def get_p0_prev_amount (self) :
        return self.new_round_state['p0_prev_amount']    

    def get_p1_prev_amount (self) :
        return self.new_round_state['p1_prev_amount']  

    def get_current_player (self) :
        return self.current_player

    def get_p0_stack (self) :
        return self.p0_stack

    def get_p1_stack (self) :
        return self.p1_stack   
    
    def get_main_pot(self) :
        return self.new_round_state['pot']['main']['amount']

    def get_side_pots(self) :
        return self.new_round_state['pot']['side']

    def current_player_uuid(self):
        return self.p0_uuid if self.current_player == 0 else self.p1_uuid

    def raise_bet(self):
        # I am not sure if i need to do an additional copy here, i am doing it just in case
        new_round_state = copy.deepcopy(self.new_round_state)
        new_add_amount = 20 if self._round_state['street'] in ['preflop', 'flop'] else 40
        new_amount = self.prev_history['amount'] + new_add_amount
        # Note, the below does not lend compatibility to the preflop street
        new_paid = 2 * new_add_amount if self.prev_history['action'] == 'RAISE' else new_add_amount

        new_round_state['pot']['main']['amount'] += new_add_amount
        new_round_state['next_player'] += 1
        new_round_state['next_player'] %= 2
        new_round_state['seats'][self.current_player]['stack'] -= new_add_amount
        new_round_state_action_histories = new_round_state['action_histories']
        
        # To be implemented for call
        if self.current_player == 0 :
            new_round_state['p0_prev_amount'] = new_amount
        else : 
            new_round_state['p1_prev_amount'] = new_amount

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

        return State(new_round_state, self.hole_card_indices, self.community_card_indices, self.is_cached)

    def fold_bet(self):
        new_round_state = copy.deepcopy(self.new_round_state)
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

        return State(new_round_state, self.hole_card_indices, self.community_card_indices, self.is_cached, True)

    def call_bet(self):
        new_round_state = copy.deepcopy(self.new_round_state)
        new_amount = self.prev_history['amount']
        if self.current_player == 0 :
            new_paid_amount = new_amount - new_round_state['p0_prev_amount']
        else :
            new_paid_amount = new_amount - new_round_state['p1_prev_amount']

        new_round_state['pot']['main']['amount'] += new_paid_amount
        new_round_state['next_player'] += 1
        new_round_state['next_player'] %= 2
        new_round_state['seats'][self.current_player]['stack'] -= new_paid_amount

        new_round_state_action_histories = new_round_state['action_histories']
        
        if self.street in new_round_state_action_histories:
            new_round_state_action_histories[self.street].append({
                'action' : 'CALL',
                'amount' : new_amount,
                'paid' : new_paid_amount,
                'uuid' : self.current_player_uuid()
            })
        else :
            new_round_state_action_histories[self.street] =[{
                'action' : 'CALL',
                'amount' : new_amount,
                'paid' : new_paid_amount,
                'uuid' : self.current_player_uuid()
            }]

        return State(new_round_state, self.hole_card_indices, self.community_card_indices, self.is_cached)


# TODO: Replace poker game actions with Enums.
# @junjie :  Is using strings better than using enums? Enums are for making the code more readable are just for efficiency?
@unique
class Action(Enum):
    FOLD = 0
    CALL = 1
    RAISE = 2


class PokerGame:

    def __init__(self, current_state=None, search_algorithm=None, evaluation_function=None):
        pass

    @staticmethod
    def actions(state):
        """Return a list of the allowable moves at this point."""
        if PokerGame.terminal_test(state):
            return []

        can_raise = True
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(state.get_new_round_state())
        # TODO: solve the bug below with p0_raises
        can_raise = state.get_current_street_raises() < 4 and \
                     (state.get_p0_raises() < 4 if state.get_current_player() == 0 else state.get_p1_raises() < 4)

        if can_raise:
            return ['FOLD', 'CALL', 'RAISE']
            # return [Action.FOLD, Action.CALL, Action.RAISE]
        else:
            return ['FOLD', 'CALL']
            # return [Action.FOLD, Action.CALL]

    @staticmethod
    def result(state, action):
        """Return the state that results from making a move from a state."""
        return {'FOLD': state.fold_bet,
                'RAISE': state.raise_bet,
                'CALL': state.call_bet}[action]()

    @staticmethod
    def add_one_more_community_card(state, card_index):
        """Return the state that results from drawing one more community card from a state."""
        new_state = copy.deepcopy(state)

        if new_state.street == 'flop':
            new_state.street = 'turn'
        elif new_state.street == 'turn':
            new_state.street = 'river'
        new_state.community_card_indices.append(card_index)

        return new_state

    @staticmethod
    def convert_index_to_card(indices):
        rank = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        suite = ['C', 'D', 'H', 'S']
        card = []
        
        for index in indices:
            rank_index = index % 13
            suite_index = (index - rank) / 13
            card.append(suite[suite_index] + rank[rank_index])

        return card

    #TODO: our agent may not always be player 0
    @staticmethod
    def utility(state):
        print(state.prev_history)
        if state.prev_history['action'] == 'FOLD':
            if state.current_player == state._round_state['next_player']: # When folding, the next player remains as the player who folded
                return - state.get_main_pot()
            else:
                return state.get_main_pot()
        elif state.prev_history['action'] == 'CALL':
            # use monte-carlo hand strength estimator
            hole_card = gen_cards(PokerGame.convert_index_to_card(state.hole_card_indices))
            community_card = gen_cards(PokerGame.convert_index_to_card(state.community_card_indices))
            win_probability = estimate_hole_card_win_rate(nb_simulation=1000, nb_player=2, hole_card=hole_card, community_card=community_card)
            expected_win = (2 * win_probability - 1) * state.get_main_pot()

            if state.current_player == state._round_state['next_player']:
                return - expected_win
            else:
                return expected_win
        else:
            raise NotImplementedError

    @staticmethod
    def terminal_test(state):
        """Return True if this is a final state for the game."""
        return state.is_terminal or (state.street == 'river' and state.prev_history['action'] == 'CALL')

import copy
import itertools
import random
from collections import namedtuple

import utils
from pypokerengine.players import BasePokerPlayer

class HonestMiniMaxPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):

        state = State(round_state, hole_card)

        if state.street == 'preflop':

            #TODO Check lookup table, fold if necessary, call if hold cards good to go
            action = 'call'

        else:

            infinity = float('inf')
            total_num_of_cards = 52

            def max_value(state):

                v = -infinity
                actions = PokerGame.actions(state) # get valid actions
                
                for action in actions :

                    if action == 'FOLD' :
                        pot_size = state['pot']['main']['amount']
                        v = max(v, -pot_size)
                        state.switch_player()

                    elif action == 'CALL' : 
                        if state.prev_history['action'] == 'RAISE':
                            v = max(v, chance_node(state))
                        else:
                            v = max(v, min_value(state))
                        state.switch_player()

                    else: # action == 'RAISE'
                        v = max(v, min_value(state))
                        state.switch_player()

                return v

            def min_value(state):

                v = infinity
                actions = PokerGame.actions(state) # get valid actions

                for action in actions :

                    if action == 'FOLD' :
                        pot_size = state['pot']['main']['amount']
                        v = min(v, pot_size)
                        state.switch_player()

                    elif action == 'CALL' :
                        if state.prev_history['action'] == 'RAISE' :         
                            v = min(v, chance_node(state))
                        else :
                            v = min(v, max_value(state))
                        state.switch_player()

                    else: # action == 'RAISE'
                        v = min(v, max_value(state))
                        state.switch_player()

                return v

            def chance_node(state):
                
                if PokerGame.terminal_test(state): # needless to draw, already 5 cc
                    return 0# TODO estimated hands value based on hold cards + community cards

                sum_chances = 0
                num_of_unknown_cards = total_num_of_cards - len(state.known_card)
                
                for i in range(total_num_of_cards):
                    if i in state.known_card:
                        continue
                    elif player is smallblind:
                        state.add_one_more_community_card(i)
                        util = max_value(state)
                    else:
                        state.add_one_more_community_card(i)
                        util = min_value(state)
                    sum_chances += util

                return sum_chances / num_of_unknown_cards

            def argmax_random_tie(seq, key=lambda x: x):
                """Return an element with highest fn(seq[i]) score; break ties at random."""
                return max(shuffled(seq), key=key)

            # return the best action based on expected minimax value:
            return argmax_random_tie(PokerGame.actions(state),
                  key=lambda a: min_value(PokerGame.result(state, action)))
        
        return action

    def receive_game_start_message(self, game_info):
        # print("\n\n")
        # pprint.pprint(game_info)
        # print("---------------------------------------------------------------------")
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        # print("My ID : "+self.uuid+", round count : "+str(round_count)+", hole card : "+str(hole_card))
        # pprint.pprint(seats)
        # print("-------------------------------")
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        # print("My ID (round result) : "+self.uuid)
        # pprint.pprint(round_state)
        # print("\n\n")
        # self.round_count = self.round_count + 1
        pass

    def setup_ai():
        return HonestMiniMaxPlayer()

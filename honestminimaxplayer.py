import copy
import itertools
import random
from collections import namedtuple

import utils.game_state
from pypokerengine.players import BasePokerPlayer
from utils import argmax, vector_add


class HonestMiniMaxPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):

        state = State(round_state)
        current_street = state['street']

        if current_street == 'preflop':

            #TODO Check lookup table, fold if necessary, call if hold cards good to go
            action = 'call'

        else:

            infinity = float('inf')
            total_num_of_cards = 52

            def max_value(state):

                v = -infinity

                actions = PokerGame.actions(state)
                
                if (actions.len == 2) :
                    valid_actions.pop(2) # Remove 'RAISE' from valid actions
                
                for action, amount in valid_actions :
                    if action == 'fold' :
                        potSize = state['pot']['main']['amount']
                        v = max(v, -potsize/2) #TODO

                    elif action == 'call' : 
                        state.mutate_to_next_player()
                        if state.prev_history['action'] == 'RAISE':
                            v = max(v, chance_node(street, knowncards, unknowncards, player, state))
                        else:
                            v = max(v, min_value(state))
                    
                    else : # action == 'RAISE'
                        v = max(v, min_value(state))
                return v

            def min_value(state):

                v = infinity

                actions = PokerGame.actions(state)

                if (actions.len == 2) :
                    valid_actions.pop(2) # Remove 'RAISE' from valid actions

                for action, amount in valid_actions :
                    # fold action:
                    if action == 'fold' :
                        potSize = state['pot']['main']['amount']
                        v = min(v, potsize/2)

                    # call action 
                    elif action == 'call' :
                        state.mutate_to_next_player()
                        if state.prev_history['action'] == 'RAISE' :         # if for consecutive RC & CC action history, check chance value
                            v = min(v, chance_node(street, knowncards, unknowncards, player, state))
                        else :
                            v = min(v, max_value(state))

                    # raise action:
                    else :                            
                        v = min(v, max_value(state))
                return v

            def chance_node(street, knowncards, unknowncards, player):
                
                if street == 'river': # needless to draw, already 5 cc
                    return 0# TODO estimated hands value based on hold cards + community cards
                if street == 'flop': # draw 1 more community cards, now 4 cc
                    nextstreet = 'turn'
                elif street == 'turn': # draw 1 more community cards, now 5 cc
                    nextstreet = 'river'

                # if not, then just aggregate all the nodes under the chance node based on bucketed probability
                sum_chances = 0
                num_of_unseen_cards = total_num_of_cards - len(knowncards)
                swap = {0: 1, 1:0}
                for card in unknowncards:
                    knowncards = knowncards.append(card)
                    unknowncards = unknowncards.remove(card)
                    if player is smallblind:
                        util = max_value(nextstreet, knowncards, unknowncards, swap[player])
                    else:
                        util = min_value(nextstreet, knowncards, unknowncards, swap[player])
                    sum_chances += util
                return sum_chances / num_of_unseen_cards

            # return the best action based on expected minimax value:
            street = state['street']
            knowncards = state['community_card'].append(hole_card)
            knowncards = hole_card.append(round_state['communty_cards'])
            unknowncards = entiredeck
            for card in knowncards:
                unknowncards.remove(card)
            state.mutate_to_next_player()

            return argmax(valid_actions, key=lambda a: chance_node(street, knowncards, unknowncards, valid_actions), default=None)
        
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

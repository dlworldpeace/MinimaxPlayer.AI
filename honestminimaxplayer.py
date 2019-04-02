import copy
import itertools
import random
from collections import namedtuple

from pypokerengine.players import BasePokerPlayer
from utils.game_state import PokerGame, State


class HonestMiniMaxPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):

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

        def convert_card_to_index(card):
            chars = list(card)
            return suite[chars[0]] + rank[chars[1]]

        hole_card_indices = []
        community_card_indices = []

        for card in hole_card:
            hole_card_indices.append(convert_card_to_index(card))
        for card in round_state['community_card']:
            community_card_indices.append(convert_card_to_index(card))

        state = State(round_state, hole_card_indices, community_card_indices)

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
                    
                    new_state = PokerGame.result(state, action)

                    if action == 'FOLD' :
                        v = max(v, -1 * PokerGame.utility(new_state))
                    elif action == 'CALL' : 
                        if state.prev_history['action'] == 'RAISE' or \
                            state.prev_history['action'] == 'CALL':
                            v = max(v, chance_node(new_state))
                        else:
                            v = max(v, min_value(new_state))
                    else: # action == 'RAISE'
                        v = max(v, min_value(new_state))

                return v

            def min_value(state):

                v = infinity
                actions = PokerGame.actions(state) # get valid actions

                for action in actions :

                    new_state = PokerGame.result(state, action)

                    if action == 'FOLD' :
                        v = min(v, PokerGame.utility(new_state))
                    elif action == 'CALL' :
                        if state.prev_history['action'] == 'RAISE' or \
                            state.prev_history['action'] == 'CALL':         
                            v = min(v, chance_node(new_state))
                        else :
                            v = min(v, max_value(new_state))
                    else: # action == 'RAISE'
                        v = min(v, max_value(new_state))

                return v

            def chance_node(state):
                
                if PokerGame.terminal_test(state): # terminal node reached
                    return PokerGame.utility(state)

                sum_chances = 0
                num_of_unknown_cards = total_num_of_cards - \
                     len(state.hole_card_indices) - len(state.community_card_indices)

                for i in range(total_num_of_cards):
                    if i in state.hole_card_indices or i in state.community_card_indices:
                        continue

                    if PokerGame.honestminimaxplayer_is_smallblind(state):
                        util = max_value(PokerGame.add_one_more_community_card(state, i))
                    else:
                        util = min_value(PokerGame.add_one_more_community_card(state, i))
                    sum_chances += util

                return sum_chances / num_of_unknown_cards

            def shuffled(iterable):
                """Randomly shuffle a copy of iterable."""
                items = list(iterable)
                random.shuffle(items)
                return items

            def argmax_random_tie(seq, key=lambda x: x):
                """Return an element with highest fn(seq[i]) score; break ties at random."""
                return max(shuffled(seq), key=key)

            # return the best action based on expected minimax value:
            return argmax_random_tie(PokerGame.actions(state),
                  key=lambda a: min_value(PokerGame.result(state, a))).lower()
        
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

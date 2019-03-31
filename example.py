from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from honestminimaxplayer import HonestMiniMaxPlayer

config = setup_config(max_round=10, initial_stack=10000, small_blind_amount=10)

config.register_player(name="HonestMiniMaxPlayer", algorithm=HonestMiniMaxPlayer())
config.register_player(name="AlwaysRaisePlayer", algorithm=RaisedPlayer())

game_result = start_poker(config, verbose=1)

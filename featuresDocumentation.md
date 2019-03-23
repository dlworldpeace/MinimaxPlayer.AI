### Original feature array
- hole_values
- hole_suits
- river_values
- river_suits
- total\_pot\_as\_bb
- own\_stack\_size
	- _NOTE THAT the player's stack size is always in relation to the big blind amount_
- other\_players\_stack\_sizes
	- Array of other player's stack sizes. The array index does not correspond to the player's index, but rather the order of player going next.
	- ie. If current player = 1, then array's values are for players 2, 3, 0
	- 012 -> 123 -> 230 -> ...
- player_folds
	- 1 if player has folded, 0 if not.
	- Order of players is similar to `other\_players\_stack\_sizes`
- money\_since\_our\_last\_move
- ~~amt\_to\_call~~
- ~~min_raise~~
- ~~max_raise~~

---
## TODOs
4. Improve features

done:
1. All the TODOs above
2. Double check stack size in `other\_players\_stack\_sizes` (doesnt seem to tally)
3. Check if the right values are gathered for a 2 player environment (`other\_players\_stack\_sizes` and `player_folds`)




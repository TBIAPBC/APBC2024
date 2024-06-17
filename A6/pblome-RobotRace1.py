#!/usr/bin/env python3

from game_utils import Direction as D
from game_utils import TileStatus
from game_utils import Map


class NaivePlayer(object):
	def reset(self, player_id, max_players, width, height):
		self.player_name = "NaiveRobot"
		self.ourMap = Map(width, height)

	def round_begin(self, r):
		pass

	def move(self, status):
		ourMap = self.ourMap
		for x in range(ourMap.width):
			for y in range(ourMap.height):
				if status.map[x, y].status != TileStatus.Unknown:
					ourMap[x, y].status = status.map[x, y].status
		# update the stored map information
 
		neighbours = []
		occupied_neighbours = []
		for d in D: # D = Direction
			diff = d.as_xy()
			coord = status.x + diff[0], status.y + diff[1]
			if coord[0] < 0 or coord[0] >= status.map.width:
				continue
			if coord[1] < 0 or coord[1] >= status.map.height:
				continue
			# make sure we don't walk out of the map
			tile = ourMap[coord]
			if tile.status == TileStatus.Unknown or tile.status == TileStatus.Empty:
				obj = tile.obj
				if obj is not None and obj.is_player():
					occupied_neighbours.append((d,coord))
					# make an extra list for tiles occupied by a different player				
    	# doesn't work right now, because obj is None even if there is a player
				else:
					neighbours.append((d, coord))   

		if len(neighbours) == 0:
			if len(occupied_neighbours) == 0:
    			# I chose to always do nothing when there are no tiles that can be reached, since we are stuck anyway
				return [] 
			else:
				tiles = occupied_neighbours
		else:
			tiles = neighbours

		assert len(status.goldPots) > 0
		gLoc = next(iter(status.goldPots))
		dists = []
		for d, coord in tiles:
			dist = abs(gLoc[0] - coord[0]) + abs(gLoc[1] - coord[1])
			dists.append((d, dist))
		d, dist = min(dists, key=lambda p: p[1])
		return [d]	

	def set_mines(self, status):
		raise NotImplementedError("'setting mines' not implemented in '%s'." % self.__class__)


# I now want to include the possibility to make more than 1 step in a round
class FasterPlayer(object):
	def reset(self, player_id, max_players, width, height):
		self.player_name = "FasterTestRobot"
		self.ourMap = Map(width, height)

	def round_begin(self, r):
		pass
	
	def move(self, status):

		ourMap = self.ourMap
		for x in range(ourMap.width):
			for y in range(ourMap.height):
				if status.map[x, y].status != TileStatus.Unknown:
					ourMap[x, y].status = status.map[x, y].status

		nextpos = status.x, status.y

		moves = []
		while len(moves) < 2: # makes up to k moves for len(moves) < k
		# chose to do two moves to have an adequate cost-gain relation
			neighbours = []
			occupied_neighbours = []
			for d in D: # D = Direction
				diff = d.as_xy()

				xcoord = nextpos[0] + diff[0]
				ycoord = nextpos[1] + diff[1]
				
				if xcoord < 0 or xcoord >= status.map.width:
					continue
				if ycoord < 0 or ycoord >= status.map.height:
					continue
				coord = xcoord, ycoord
				tile = ourMap[coord]
				if tile.status == TileStatus.Unknown or tile.status == TileStatus.Empty:
					obj = tile.obj
					if obj is None: # includes occupied tiles as well 
						neighbours.append((d,coord))
					elif obj.is_player(): # doesn't work yet
						occupied_neighbours.append((d,coord))

			if len(neighbours) == 0:
				if len(occupied_neighbours) == 0:
					if not moves:
						return ['UP']
					else: 
						return moves
				else:
					tiles = occupied_neighbours
			else:
				tiles = neighbours
    
			assert len(status.goldPots) > 0
			gLoc = next(iter(status.goldPots))
			dists = []
			for d, coord in tiles:
				dist = abs(gLoc[0] - coord[0])+ abs(gLoc[1] - coord[1])
				dists.append((d, dist))
			d, dist = min(dists, key=lambda p: p[1])

			moves.append(d)
			nextpos = nextpos[0] + d.as_xy()[0], nextpos[1] + d.as_xy()[1]
		return moves

	def set_mines(self, status):
		raise NotImplementedError("'setting mines' not implemented in '%s'." % self.__class__)

# the faster player always loses against the "slower" player somehow



# I wanted to test how well a non-moving robot would do, since he wouldn't spend gold on moves and gain 1 gold every round
class StationaryPlayer(object):
	def reset(self, player_id, max_players, width, height):
		self.player_name = "StationaryRobot"
		self.ourMap = Map(width, height)

	def round_begin(self, r):
		pass

	def move(self, status):
		return []

	def set_mines(self, status):
		raise NotImplementedError("'setting mines' not implemented in '%s'." % self.__class__)



players = [NaivePlayer(), FasterPlayer(), StationaryPlayer()]


"""Result:
a - Test - NonRandomPlayer
b - Test - RandomPlayer
c - pblome - NaivePlayer
d - pblome - FasterPlayer
e - pblome - StationaryPlayer

Player   Health   Gold      Position
a        100      1274      8,8
b        55       1         3,28
c        100      1139      10,9
d        100      1         12,10
e        100      1099      16,7

Player   Health   Gold      Position
a        100      579       22,26
b        60       0         16,29
c        100      1229      21,7
d        100      1         25,10
e        100      1099      8,20

Player   Health   Gold      Position
a        100      862       22,23
b        100      1         8,24
c        58       1019      16,21
d        59       877       17,20
e        100      1099      23,20

Player   Health   Gold      Position
a        100      1816      5,14
b        5        1         18,25
c        100      1051      6,21
d        100      321       14,12
e        100      1099      4,3

NaivePlayer is pretty much as good as the NonRandomPlayer from the Test file
Surprisingly, the stationary player as well but the faster player is barely any better than the RandomPlayer
"""

#!/usr/bin/env python3
import math 
from collections import deque

from game_utils import Direction as D
from game_utils import TileStatus
from game_utils import Map, GameParameters


class DPPlayer(object):
    
    
    def reset(self, player_id, max_players, width, height):
        self.player_name = "FirstTestRobot"
        self.ourMap = Map(width, height)
        self.round_counter = 0
        self.gold_pot_reset_round = 0 
        self.last_gold_pot_location = None
        self.params = GameParameters()

    def round_begin(self, r):
        self.round_counter = r
        # I introduced a variable storing when the gold pot has been reset
        if (self.round_counter - self.gold_pot_reset_round) >= self.params.goldPotTimeOut:
            self.gold_pot_reset_round = self.round_counter  
    
    def move(self, status):
        visited = set() # keep track of visited nodes to avoid loops (e.g. up-down-up-down)
        ourMap = self.ourMap
        for x in range(ourMap.width):
            for y in range(ourMap.height):
                if status.map[x, y].status != TileStatus.Unknown:
                    ourMap[x, y].status = status.map[x, y].status
                    visited.add((x,y))
        curpos = (status.x,status.y)
        
        assert len(status.goldPots) > 0
        gLoc = next(iter(status.goldPots))
        
        if self.last_gold_pot_location and gLoc != self.last_gold_pot_location:
            self.gold_pot_reset_round = self.round_counter
        
        self.last_gold_pot_location = gLoc
        
        def shortestpath(goldpos):
            m = status.map.width
            n = status.map.height
            dists = [[math.inf for _ in range(m)] for _ in range(n)]
            dists[goldpos[0]][goldpos[1]] = 0            
            
            # fill the distance matrix by BFS approach
            queue = deque([goldpos])
            
            while queue:
                pos = queue.popleft()
                current_dist = dists[pos[0]][pos[1]]
                
                for direction in D:
                    x,y = direction.as_xy()
                    new_pos = pos[0] + x, pos[1] + y
                    
                    if 0 <= new_pos[0] < m and 0 <= new_pos[1] < n:
                        if dists[new_pos[0]][new_pos[1]] == math.inf: #otherwise shorter distance has already been found
                            if not ourMap[new_pos[0], new_pos[1]].status.is_blocked():# != TileStatus.Wall: # otherwise keep inf
                                dists[new_pos[0]][new_pos[1]] = current_dist + 1
                                queue.append((new_pos[0], new_pos[1]))
            
            return dists
        
        def path(curpos, dists):
            
            num_moves = dists[curpos[0]][curpos[1]]
            goldPotRemainingRounds = self.params.goldPotTimeOut - (self.round_counter - self.gold_pot_reset_round) -1

            if num_moves > goldPotRemainingRounds:
                # We can't reach gold in time, so we dn't move to save gold.
                return []
            else:
                pos = curpos
                max_iterations = 8 
                # we maximally want to do ca. 8 iterations, otherwise the moves get to expensive at once
                counter = 0
                moves = []
                while counter < max_iterations and len(moves) < num_moves:
                    for d in D:
                        diff = d.as_xy()
                        coord = pos[0] + diff[0], pos[1] + diff[1]
                        if coord[0] < 0 or coord[0] >= status.map.width:
                            continue
                        if coord[1] < 0 or coord[1] >= status.map.height:
                            continue
                        if dists[coord[0]][coord[1]] == dists[pos[0]][pos[1]] -1:
                            moves.append(d)
                            pos = coord[0], coord[1]
                            break
                    counter += 1
                return moves

        moves = []
        for _ in range(4): # allow up to 4 moves while exploring the map
            neighbours = []
            for d in D:
                diff = d.as_xy()
                new_pos = curpos[0] + diff[0], curpos[1] + diff[1]
                
                if 0 <= new_pos[0] < ourMap.width and 0 <= new_pos[1] < ourMap.height and new_pos not in visited:
                    tile = ourMap[new_pos[0], new_pos[1]]
                    if tile.status == TileStatus.Unknown or tile.status == TileStatus.Empty:
                        neighbours.append((d, new_pos))
            # neighbours stores all reachable tiles from current position

            if len(neighbours) == 0:
                break

            move = neighbours[0][0]
            if move:
                moves.append(move)
                diff = move.as_xy()
                curpos = curpos[0] + diff[0], curpos[1] + diff[1]
                visited.add(curpos)

        if moves:
            return moves      
        dists = shortestpath(gLoc)
        moves= path(curpos, dists)
        return moves
               
    def set_mines(self, status):
        # sets mines around a neighbouring player
        map = status.map
        x,y = status.x,status.y
        mines = []
        victim = None
        for d in D:
            diff = d.as_xy()
            neighbour = x+diff[0], y+diff[1]
            if 0 <= neighbour[0] < map.width and 0 <= neighbour[1] < map.height and status.map[neighbour].obj is not None:
                if status.map[neighbour].obj.is_player():
                    victim = neighbour
        if victim:
            for d in D:
                diff = d.as_xy()
                tile = victim[0]+diff[0], victim[1]+diff[1]
                if status.map[tile].obj is None and not status.map[tile].status.is_blocked():
                    # no wall, mine or player
                    mines.append(tile)              
        return mines
          
  
players = [DPPlayer()]


"""
Results:
a - Test - NonRandom
b - Test - Random
c - Beatme
d - pblome - DPPlayer

6x6:

Player   Health   Gold      Position
a        98       13939     5,3
b        23       0         2,4
c        100      6351      5,5
d        28       8017      2,3

Player   Health   Gold      Position
a        100      9586      3,3
b        85       0         1,4
c        100      10930     4,2
d        73       19835     2,3

Player   Health   Gold      Position
a        100      9955      3,5
b        60       0         2,4
c        95       11201     4,2
d        39       18441     3,4

30x30:

Player   Health   Gold      Position
a        100      988       2,28
b        25       0         29,15
c        100      2535      26,29
d        100      2950      9,1

-> map is explored by round 44 

Player   Health   Gold      Position
a        100      1024      13,12
b        100      0         8,28
c        100      3017      10,0
d        100      3469      0,23


Player   Health   Gold      Position
a        100      1263      14,14
b        85       2         22,29
c        100      2520      22,22
d        100      3880      4,5
"""
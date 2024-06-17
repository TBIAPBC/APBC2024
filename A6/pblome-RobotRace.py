#!/usr/bin/env python3
import math 
from collections import deque

from game_utils import Direction as D
from game_utils import TileStatus
from game_utils import Map, GameParameters


class DPPlayer(object):
    
    
    def reset(self, player_id, max_players, width, height):
        self.player_name = "pblome"
        self.ourMap = Map(width, height)
        self.round_counter = 0
        self.gold_pot_reset_round = 0 
        self.last_gold_pot_location = None
        self.params = GameParameters()
        self.jumps_allowed = False
        self.start_pos = (-1,-1)

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
                    #visited.add((x,y))
        curpos = (status.x,status.y)
        visited.add(curpos)
        
        # we want to find out if jumping over walls is allowed
        if self.round_counter == 1:
            self.start_pos = curpos
            neighbour_found = False
            for d in D:
                diff = d.as_xy()
                neighbour = curpos[0]+diff[0], curpos[1]+diff[1]
                if 0 <= neighbour[0] < ourMap.width and 0 <= neighbour[1] < ourMap.height:
                    if status.map[neighbour].status == TileStatus.Wall:
                        behind_wall = neighbour[0]+diff[0], neighbour[1]+diff[1]
                        if 0 <= behind_wall[0] < ourMap.width and 0 <= behind_wall[1] < ourMap.height:
                            if status.map[behind_wall].status == TileStatus.Empty and (status.map[behind_wall].obj is None or status.map[behind_wall].obj.is_gold()):
                                neighbour_found = True
                                return [d,d]
            if not neighbour_found:
                return []                

        # are we behind the wall or did we crash?
        if self.round_counter ==2:
            if curpos != self.start_pos:
                self.jumps_allowed = True

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
            
            queue = deque([goldpos])
            
            while queue:
                pos = queue.popleft()
                current_dist = dists[pos[0]][pos[1]]
                
                for direction in D:
                    x,y = direction.as_xy()
                    new_pos = pos[0] + x, pos[1] + y
                    
                    if 0 <= new_pos[0] < m and 0 <= new_pos[1] < n:
                        if dists[new_pos[0]][new_pos[1]] == math.inf: #otherwise shorter distance has already been found
                            if not ourMap[new_pos[0], new_pos[1]].status.is_blocked():
                                dists[new_pos[0]][new_pos[1]] = current_dist + 1
                                queue.append((new_pos[0], new_pos[1]))
            
            return dists
        
        def path(curpos, dists):
            
            num_moves = dists[curpos[0]][curpos[1]]
            goldPotRemainingRounds = self.params.goldPotTimeOut - (self.round_counter - self.gold_pot_reset_round) -1

            if num_moves > goldPotRemainingRounds:
                # We can't reach gold in time, so we don't move to save gold.
                if self.jumps_allowed:
                    for d in D:
                        diff = d.as_xy()
                        neighbour = curpos[0]+diff[0], curpos[1]+diff[1]
                        if 0 <= neighbour[0] < ourMap.width and 0 <= neighbour[1] < ourMap.height:
                            if status.map[neighbour].status == TileStatus.Wall:
                                behind_wall = neighbour[0]+diff[0], neighbour[1]+diff[1]
                                if 0 <= behind_wall[0] < ourMap.width and 0 <= behind_wall[1] < ourMap.height:
                                    if status.map[behind_wall].status == TileStatus.Empty and (status.map[behind_wall].obj is None or status.map[behind_wall].obj.is_gold()):
                                        if dists[behind_wall[0]][behind_wall[1]] + 5 <= goldPotRemainingRounds:
                                            moves = [d,d]+path(behind_wall, dists)
                                            return moves
                return []
                """
                # runs way better without
                # move into the middle of the map instead to have a better starting point for next round 
                moves = []
                for _ in range(2):
                    neighbours = []
                    for d in D:
                        diff = d.as_xy()
                        newpos =  curpos[0]+diff[0], curpos[1]+diff[1]
                        if 0 <= newpos[0] < ourMap.width and 0 <= newpos[1] < ourMap.height:
                            tile = ourMap[newpos[0], newpos[1]]
                            if tile.status == TileStatus.Empty or tile.status ==TileStatus.Unknown:
                            #if not tile.status.is_blocked():
                                neighbours.append((newpos,d))
                    dists = []
                    middle_x = ourMap.width // 2
                    middle_y = ourMap.height //2
                    for coord, dir in neighbours:
                        dist = abs(coord[0]-middle_x)+abs(coord[1]-middle_y)
                        dists.append((dir, coord, dist))
                    dists = sorted(dists, key= lambda x: x[2])
                    #(f"dists:{dists}")
                    dir, coord, dist = dists[0]
                    moves.append(dir)
                    curpos = coord
                return moves"""
            else:
                pos = curpos
                max_iterations = 8
                # we maximally want to do ca. 8 iterations, otherwise the moves get to expensive at once
                counter = 0
                moves = []
                while counter < max_iterations and len(moves) < num_moves:
                    if self.jumps_allowed:
                        for d in D:
                            diff = d.as_xy()
                            neighbour = curpos[0]+diff[0], curpos[1]+diff[1]
                            if 0 <= neighbour[0] < ourMap.width and 0 <= neighbour[1] < ourMap.height:
                                if status.map[neighbour].status == TileStatus.Wall:
                                    behind_wall = neighbour[0]+diff[0], neighbour[1]+diff[1]
                                    if 0 <= behind_wall[0] < ourMap.width and 0 <= behind_wall[1] < ourMap.height:
                                        if status.map[behind_wall].status == TileStatus.Empty and (status.map[behind_wall].obj is None or status.map[behind_wall].obj.is_gold()):
                                            if dists[behind_wall[0]][behind_wall[1]] + 5 <= dists[pos[0]][pos[1]]:
                                                moves = [d,d]+path(behind_wall, dists)
                                                pos = behind_wall
                                                counter += 1
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

        """
        # algorithm works better without an explicit exploration phase
        moves = []
        for _ in range(4): 
            neighbours = []
            for d in D:
                diff = d.as_xy()
                new_pos = curpos[0] + diff[0], curpos[1] + diff[1]
                
                if 0 <= new_pos[0] < ourMap.width and 0 <= new_pos[1] < ourMap.height and new_pos not in visited:
                    tile = ourMap[new_pos[0], new_pos[1]]
                    if tile.status == TileStatus.Unknown:# or tile.status == TileStatus.Empty:
                        neighbours.append((d, new_pos))

            if len(neighbours) == 0:
                break
            
            dists=[]
            for dir, coord in neighbours:
                dist = abs(coord[0]-gLoc[0])+abs(coord[1]-gLoc[1])
                dists.append((dir, coord, dist))
            dists = sorted(dists, key= lambda x: x[2])
                    
            #move = neighbours[0][0]
            move = []
            for i in range(len(dists)):
                if status.map[dists[i][1]].obj is None or not status.map[dists[i][1]].obj.is_player():
                    move = dists[i][0]
                    break
            if move:
                moves.append(move)
                diff = move.as_xy()
                curpos = curpos[0] + diff[0], curpos[1] + diff[1]
                visited.add(curpos)

        if moves:
            return moves  """

        dists = shortestpath(gLoc)
        moves= path(curpos, dists)
        return moves
    
    
    def set_mines(self, status):
        
        assert len(status.goldPots) > 0
        gLoc = next(iter(status.goldPots))
        curpos = (status.x,status.y)
       
        return []
            
        
        """ 
        # sets mines close to the gold 
        # always costs too much gold and thus worse results
        mines = []
        if abs(curpos[0]-gLoc[0]) > 3 or abs(curpos[1]-gLoc[1]) > 3:
            valid_neighbours = []
            for d in D:
                diff = d.as_xy()
                newpos = gLoc[0]+diff[0], gLoc[1]+diff[1]
                if 0 <= newpos[0] < status.map.width and 0 <= newpos[1] < status.map.height:
                    if status.map[newpos].obj is None and not status.map[newpos].status.is_blocked():
                        return [newpos]
                
        return mines
        # sets mines around a neighbouring player
        # with the new mine options also dangerous for my own player
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
                if 0 <= tile[0] < map.width and 0 <= tile[1] < map.height:
                    if status.map[tile].obj is None and not status.map[tile].status.is_blocked():
                    # no wall, mine or player
                        mines.append(tile)              
        return mines"""
  
players = [DPPlayer()]


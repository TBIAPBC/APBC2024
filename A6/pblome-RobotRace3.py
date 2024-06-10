#!/usr/bin/env python3
import math 
from collections import deque

from game_utils import Direction as D
from game_utils import TileStatus
from game_utils import Map, GameParameters


class DPPlayer2(object):
    
    
    def reset(self, player_id, max_players, width, height):
        self.player_name = "FirstTestRobot"
        self.ourMap = Map(width, height)
        self.round_counter = 0
        self.gold_pot_reset_round = 0 
        self.last_gold_pot_location = None
        self.params = GameParameters()
        self.stack = []
        self.visited = []
        self.path = []

    def round_begin(self, r):
        self.round_counter = r
        # I introduced a variable storing when the gold pot has been reset
        if (self.round_counter - self.gold_pot_reset_round) >= self.params.goldPotTimeOut:
            self.gold_pot_reset_round = self.round_counter  
    
    def move(self, status):
        visited = self.visited # keep track of visited nodes to avoid loops (e.g. up-down-up-down)
        stack = self.stack
        ourMap = self.ourMap
        for x in range(ourMap.width):
            for y in range(ourMap.height):
                if status.map[x, y].status != TileStatus.Unknown:
                    ourMap[x, y].status = status.map[x, y].status
        curpos = (status.x,status.y)
        if len(self.path) ==0:
            self.path.append(curpos) # need to include the starting position in the path
        

        path_index = self.path.index(curpos)
        ## PROBLEM:
        # curpos is not in the path if it was visited and then we reversed back
        # but a crash occurred in this position before the retracing took place
        if self.path[-1] != curpos:
            self.path = self.path[:path_index+1]
            neighbours = []
            for i in range(len(self.path)):
                if self.path[i] in stack:
                    stack.remove(self.path[i])
                    visited.remove(self.path[i])
                for d in D:
                    diff = d.as_xy()
                    neighbours.append((self.path[i][0]+diff[0], self.path[i][1]+diff[1]))
                        # store only the neighbours that would be reachable from any position in the current path
            removing = []
            for coord in stack:
                if coord not in neighbours:
                    removing.append(coord)
                elif ourMap[coord].status == TileStatus.Wall:
                    removing.append(coord)
                elif coord in self.path:
                    removing.append(coord)

            for coord in removing:
                stack.remove(coord)
            removing2 = []
            for coord in visited:
                if coord not in neighbours:
                    removing2.append(coord)
            for coord in removing2:
                visited.remove(coord)
                            
        if len(self.path) >1 and curpos not in self.path:
            self.path.append(curpos)     
            
        for pos in stack:
            processd = True
            for d in D:
                diff = d.as_xy()
                new_pos = pos[0] + diff[0], pos[1] + diff[1]
                if 0 <= new_pos[0] < ourMap.width and 0 <= new_pos[1] < ourMap.height:
                    if ourMap[new_pos].status != TileStatus.Wall and new_pos not in stack and new_pos not in visited:# and new_pos not in neighbours:
                        processd = False
                        # if something in the vicinity is not known processed by DFS yet, leave in stack
                        # otherwise remove to avoid unnecessary explorations
            if processd == True:
                stack.remove(pos)
                if pos not in visited:
                    visited.append(pos)   

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
                
                for d in D:
                    x,y = d.as_xy()
                    new_pos = pos[0] + x, pos[1] + y
                    
                    if 0 <= new_pos[0] < m and 0 <= new_pos[1] < n:
                        if dists[new_pos[0]][new_pos[1]] == math.inf: #otherwise shorter distance has already been found
                            if ourMap[new_pos[0], new_pos[1]].status != TileStatus.Wall: # otherwise keep inf
                                dists[new_pos[0]][new_pos[1]] = current_dist + 1
                                queue.append((new_pos[0], new_pos[1]))
            
            return dists
        
        def path(curpos, dists):
            
            num_moves = dists[curpos[0]][curpos[1]]
            goldPotRemainingRounds = self.params.goldPotTimeOut - (self.round_counter - self.gold_pot_reset_round) -1

            if num_moves > goldPotRemainingRounds:
                # We can't reach gold in time, so we don't move to save gold.
                return []
                # maybe move innto the middle of the map instead to have a better starting point for next round ??
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
            
            
        def dfs_explore(stack, processed, curpos, gLoc):
            moves = []
            while len(moves) <4:
                if curpos not in processed:
                    processed.append(curpos)
                possible_moves = []
                for d in D: # maybe don't append to the stack in the order of D, but such that the closest to the gold is first
                    diff = d.as_xy()
                    new_pos = curpos[0] + diff[0], curpos[1] + diff[1]

                    if 0 <= new_pos[0] < ourMap.width and 0 <= new_pos[1] < ourMap.height:
                        if new_pos not in stack and new_pos not in processed and new_pos not in self.path:
                            tile = ourMap[new_pos[0], new_pos[1]]
                            if tile.status == TileStatus.Empty or tile.status ==TileStatus.Unknown:
                                possible_moves.append(new_pos)
                dists = []
                for coord in possible_moves:
                    dist = abs(coord[0]-gLoc[0])+abs(coord[1]-gLoc[1])
                    dists.append((coord, dist))
                dists = sorted(dists, key= lambda x: x[1])
                for coord, dist in dists: # append occupied tiles first to include them in the stack, but not as the last entry to prefer other tiles first
                    if status.map[coord].obj is not None and status.map[coord].obj.is_player():
                        stack.append(coord)
                    else:
                        continue
                        
                for coord, dist in dists:
                    if coord not in stack:
                        stack.append(coord)
                # reorder the neighbours to be added this iteration
                # according to their distance to the gold pot
                if len(stack) == 0:
                    break
                
                nextpos = stack[-1]
                if len(moves) == 0:
                    if status.map[nextpos].obj is not None and status.map[nextpos].obj.is_player():
                    # next position is occupied, most likely leads to a crash
                    # take next in line in stack
                    # only check this for the first move, because hopefully the robot has moved by the second move
                        nextpos = stack[-2]
                
                if nextpos in moves:
                    for i in range(len(stack)-1, 0,-1):
                        if stack[i] in moves:
                            continue
                        else:
                            index = i
                            break
                    nextpos = stack[index]

                
                moves.append(nextpos)
                if nextpos not in processed:
                    processed.append(nextpos)
                curpos = nextpos

            return moves, stack, processed
                                
        explored = True
        for x in range(ourMap.width):
            for y in range(ourMap.height):
                if status.map[x, y].status == TileStatus.Unknown:
                    explored = False
                    break
        
        if explored:
            print("Map is explored")
            dists = shortestpath(gLoc)
            moves= path(curpos, dists)
            return moves
        else:
            moves_coords, stacks, processed = dfs_explore(stack, visited, curpos, gLoc)
            visited = processed            
            self.stack = stacks 

                    
        if moves_coords:
            moves = []
            for i in range(len(moves_coords)):
                x = moves_coords[i][0] - curpos[0] 
                y = moves_coords[i][1] - curpos[1]
                # what if the tile to be explored (that was last in the stack) was not in the direct vicinity, but we need more steps
                # check what the difference is (-1,0) or (-2,1) etc
                target = moves_coords[i]
                if abs(x)>1 or abs(y)>1:
                    mult_moves = []
                    while abs(x)>1 or abs(y)>1:
                        predecessor = self.path.pop()
                        x = target[0] - predecessor[0] 
                        y = target[1] - predecessor[1]
                        mult_moves.append(predecessor)
                    self.path.append(predecessor)
                    mult_moves.append(target)
                    for j in range(len(mult_moves)): #convert coordinates into directions
                        x_ = mult_moves[j][0] - curpos[0] 
                        y_ = mult_moves[j][1] - curpos[1]
                        for d in D:
                            diff = d.as_xy()
                            newpos = curpos[0]+diff[0], curpos[1]+diff[1]
                            if diff == (x_,y_):
                                moves.append(d)
                                curpos = newpos
                    curpos = moves_coords[i]          
                else:    
                    for d in D:
                        diff = d.as_xy()
                        newpos = curpos[0]+diff[0], curpos[1]+diff[1]
                        if diff == (x,y):
                            moves.append(d)
                            curpos = newpos
                if moves_coords[i] not in self.path:
                    self.path.append(moves_coords[i])
            
            return moves 
        else:
            return []

               
    def set_mines(self, status):
        raise NotImplementedError("'setting mines' not implemented in '%s'." % self.__class__)
  
  
players = [DPPlayer2()]



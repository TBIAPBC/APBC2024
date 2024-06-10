#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import random
from game_utils import nameFromPlayerId
from game_utils import Direction as D, MoveStatus
from game_utils import Tile, TileStatus, TileObject
from game_utils import Map, Status
from simulator import Simulator
from player_base import Player
from shortestpaths import AllShortestPaths


class NaivePlayer(Player):
    def reset(self, player_id, max_players, width, height):
        
        self.player_name = "Naive player Adlhart"
        self.moves = [D.up, D.left, D.down, D.right, D.up, D.up_left, D.down_left,
						D.down_right, D.up_right]
    
        
        
    def round_begin(self, r):
        
        pass

    def set_mines(self, status):
        return []
    
    
    def get_gold_direction(self, status, x, y): 
        # get preferred directions for pot of gold
        gold_pots_coordinates = list(status.goldPots.keys())
        
        x_gold, y_gold = gold_pots_coordinates[0]
        
        distance_x = x - x_gold
        distance_y = y - y_gold
        directions = []
        if distance_x < 0: 
            directions.append(D.right)
        
            if distance_y < 0: 
                directions.append(D.up_right)
                directions.append(D.up)
            elif distance_y > 0:
                directions.append(D.down_right)
                directions.append(D.down)
         
        elif distance_x > 0 :
            directions.append(D.left)
        
            if distance_y < 0: 
                directions.append(D.up_left)
                directions.append(D.up)
            elif distance_y > 0:
                directions.append(D.down_left)
                directions.append(D.down)
            
        elif distance_x == 0: 
            if distance_y < 0: 
                directions.append( D.up )
            else: 
                directions.append(  D.down)
      
        return directions
        
    def move(self, status): 
        
        
        gold_pots_coordinates = list(status.goldPots.keys())
        x_gold, y_gold = gold_pots_coordinates[0]
        
        if abs(x_gold - status.x) + abs(y_gold - status.y) > status.gold/2:
            num_moves = 0
        else:     
            num_moves = 2
        
        
        directions = []
        newx = status.x
        newy = status.y
        
        for n in range(num_moves):
            
            # try to move closer to gold if blocked make random move
            gold_directions = self.get_gold_direction(status, newx, newy)
            
            for gold_direction in gold_directions:
                gold_x, gold_y = gold_direction.as_xy()
                
                if newx+gold_x < 0 or newx+gold_x >= self.status.map.width:
                    continue
                if newy+gold_y < 0 or newy+gold_y >= self.status.map.height:
                    continue
                
                if not status.map.__getitem__([newx+gold_x, newy+gold_y]).is_blocked():       
                    directions.append(gold_direction)
                    newx  += gold_x
                    newy  += gold_y
                    break
            
            else:
              
                indices = [i for i in range(len(self.moves))]
                random.shuffle(indices)
                
                for move_index in indices: 
                    direction = self.moves[move_index]
                    d = direction.as_xy()
                    
                    if newx+d[0] < 0 or newx+d[0] >= self.status.map.width:
                        continue
                    if newy+d[1] < 0 or newy+d[1] >= self.status.map. height:
                        continue
                         
                    if not status.map.__getitem__([newx+d[0], newy+d[1]]).is_blocked():

                        directions.append(direction)
                        newx  += d[0]
                        newy  += d[1]
                      
                        break
           
        return directions
         
class TestPlayer(Player):

        
    def reset(self, player_id, max_players, width, height):
        
        self.player_name = "Test player Adlhart"
        self.ourMap = Map(width, height)
        
        self.distance_cutoff = 0.85
        self.other_best_paths = []
        self.last_gLoc = None
        self.wait_next_gold = False
        self.center = (int(width/2), int(height/2))
        self.numMoves = 5
        
    def get_cost(self, NumMoves): 
        s = 0 
        for i in range(NumMoves): 
            s += i+1
        return s
    
    def check_others(self, status):
        
        # get shortest paths of all other visible players
        gLoc = list(status.goldPots.keys())[0]   
        other_paths = []
       
        for other in self.status.others: 
            if other != None:
                position_other = (other.x, other.y)
                paths = AllShortestPaths(gLoc, self.ourMap)
                bestpath = paths.shortestPathFrom(position_other)
                bestpath.append(gLoc)
                other_paths.append(bestpath)
              
                
        return other_paths   
    
    def _as_direction(self,curpos,nextpos):
        for d in D:
                diff = d.as_xy()
                if (curpos[0] + diff[0], curpos[1] + diff[1]) ==  nextpos:
                        return d
        return None

    def _as_directions(self,curpos,path):
        return [self._as_direction(x,y) for x,y in zip([curpos]+path,path)]
    
    
    def round_begin(self, r):
        status = self.status
        
        # update map 
        for x in range(self.ourMap.width):
            for y in range(self.ourMap.height):
                
                if status.map[x, y].status != TileStatus.Unknown:
                    self.ourMap[x, y].status = status.map[x, y].status
                    
                    # update center to some empty tile if necessary
                    if (x,y) == self.center and status.map[x, y].status != TileStatus.Empty: 
                        center_updated = False
                        j = 1
                        while center_updated == False: 
                            for xd in [-j, j, 0]: 
                                if center_updated: 
                                    break
                                for yd in [-j, j, 0]:  
                                    if status.map[x+xd, y+yd].status == TileStatus.Empty: 
                                        self.center = (x+xd, y+yd)
                                        center_updated = True
                                        break
                            j+=1
                    
        self.other_paths = self.check_others(status)
        
        self.numMoves = 5
        
        curpos = (status.x,status.y)  
        budget = status.gold
        gAmount = list(status.goldPots.values())[0]
        gLoc = list(status.goldPots.keys())[0]   
        
        
        # check if gold has moved
        if self.last_gLoc and gLoc != self.last_gLoc:
            self.wait_next_gold = False   
            
        self.last_gLoc = gLoc
      
       
        # get shortest path to gold     
        paths = AllShortestPaths(gLoc, self.ourMap)
        bestpath = paths.shortestPathFrom(curpos)[1:]
        bestpath.append(gLoc)
        distance = len(bestpath)
        cost_full_path = self.get_cost(distance)
        
        
        # check if others closer than cutoff to gold than myself, if possible
        if len(self.other_paths) > 0:
            min_other_distances = min([len(x) for x in self.other_paths])
            if min_other_distances < distance * self.distance_cutoff : 
                self.wait_next_gold = True
               
        
        # wait for next gold of too far away
        if distance/self.numMoves > status.goldPotRemainingRounds:
                self.numMoves = 0
                self.wait_next_gold = True
              
                
        # if waiting for next gold, change path to center in steps of 2
        if self.wait_next_gold: 
            self.numMoves = 2
            paths = AllShortestPaths(self.center, self.ourMap)
            
            bestpath = paths.shortestPathFrom(curpos)[1:]
            bestpath.append(self.center)
            
            if [self.center] ==  bestpath:
                bestpath = []
            
                
            
        else: 
            # go directly for gold if amount in gold less than cost of move
            if cost_full_path < budget and cost_full_path < gAmount: 
               self.numMoves = distance
    
    
     
        self.bestpath = bestpath
        
    def set_mines(self, status):
        
        
        mines = []
        

        return mines
      

        
    def move(self, status): 
        
        budget = status.gold
        curpos = (status.x,status.y)  
        path = []
        stop_path = False
    
        for i in range(min(self.numMoves, len(self.bestpath), 12)): 
            position = self.bestpath[i]
            budget -= i+1
            
            if self.ourMap[position[0], position[1]].status == TileStatus.Empty and budget > 1 : 
              
                # check if my path on others shortest path and stop if other is closer
                if len(self.other_paths) != 0:
                    for x in self.other_paths: 
                        if position in x: 
                            if x.index(position)-1 <= i: 
                                stop_path = True
                                break
            else: 
                stop_path = True
                
            if stop_path == True:
                break
            
            else: 
                path.append(position)
          
        return self._as_directions(curpos,path)
        

                
        
players = [ TestPlayer()]
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
        
      
    def get_cost(self, NumMoves): 
        s = 0 
        
        for i in range(NumMoves): 
            s+= i+1
        return s
    def round_begin(self, r):
        pass

    def set_mines(self, status):
        return []
    
    
    def _as_direction(self,curpos,nextpos):
        for d in D:
                diff = d.as_xy()
                if (curpos[0] + diff[0], curpos[1] + diff[1]) ==  nextpos:
                        return d
        return None

    def _as_directions(self,curpos,path):
        return [self._as_direction(x,y) for x,y in zip([curpos]+path,path)]
    
    
    def check_others(self, status, gLoc):
        
        positions = []
        distances = []
        for other in self.status.others: 
            if other != None:
                position_other = (other.x, other.y)
                positions.append(position_other)
                paths = AllShortestPaths(gLoc, self.ourMap)
                bestpath = paths.shortestPathFrom(position_other)
                distances.append(len(bestpath))
        
        return distances  , positions      

    def move(self, status): 
        
        maxMoves = 10
        
        # update map 
        for x in range(self.ourMap.width):
            for y in range(self.ourMap.height):
                if status.map[x, y].status != TileStatus.Unknown:
                    self.ourMap[x, y].status = status.map[x, y].status
                    
  
        curpos = (status.x,status.y)  
        budget = status.gold
        gAmount = list(status.goldPots.values())[0]
        gLoc = list(status.goldPots.keys())[0]    
       
        
        paths = AllShortestPaths(gLoc, self.ourMap)
        bestpath = paths.shortestPathFrom(curpos)[1:]
        bestpath.append(gLoc)
        distance= len(bestpath)
        cost_full_path = self.get_cost(distance)
        other_distances, other_positions = self.check_others( status, gLoc)
        
        
        
        if len(other_distances) != 0:
           if min(other_distances) < distance/1.5: 
               maxMoves = 0
              
        
        if maxMoves > 0:
            if cost_full_path < budget and cost_full_path < gAmount : 
                maxMoves = distance
            else: 
                if distance/maxMoves > status.goldPotRemainingRounds:
                        maxMoves = 0
                       
                        
        path = []
        
        for i in range(min(maxMoves, distance)): 
            position = bestpath[i]
            budget -= i+1
           
            if self.ourMap[position[0], position[1]].status == TileStatus.Empty and budget > 1: 
                if position not in other_positions:
                    path.append(position)
                else: 
                    break
                    
            else: 
                break
        
        return self._as_directions(curpos,path)
                
        
players = [NaivePlayer(), 
          TestPlayer()]
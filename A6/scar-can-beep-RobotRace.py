#!/usr/bin/env python3
import random
import heapq

from game_utils import nameFromPlayerId
from game_utils import Direction as D, MoveStatus
from game_utils import Tile, TileStatus, TileObject
from game_utils import Map, Status
from simulator import Simulator
from player_base import Player

#CLASS
class ScarsPathfindingPlayer(Player):
    '''
    This Player uses Dijkstra algorithm to find the gold 
    (but only makes one step per round)
    '''
    def reset(self, player_id, max_players, width, height):
        self.player_name = "Scar_Pathfinder"
        self.ourMap = Map(width, height)
        self.path = [] 

    def round_begin(self, r):
        '''
        Called at the beginning of each round
        '''
        print(f"Starting round {r}")

    def set_mines(self, status):
        '''Possibly set mine logic for later'''
        return []

    def move(self, status):
        '''
        Updates the internal map with the visible tiles then finds gold 
        and calculate path there. If we get a path we move according to path.
        If not we choose a random direction.
        '''
        for x in range(self.ourMap.width):
            for y in range(self.ourMap.height):
                if status.map[x, y].status != TileStatus.Unknown:
                    self.ourMap[x, y].status = status.map[x, y].status

        
        target = self.find_nearest_gold(status)

        if target:
            self.path = self.calculate_path(status, target)
            
        if self.path:
            next_move = self.path.pop(0)
            return [next_move]

        return [random.choice(self.get_possible_moves(status))]

    def find_nearest_gold(self, status):
        '''
        Finds nearest gold (if it exists) and calls function to retrieve manhattan distance
        '''
        if status.goldPots:
            return min(status.goldPots.keys(), key=lambda loc: self.manhattan_distance((status.x, status.y), loc))
        return None

    def calculate_path(self, status, target):
        '''
        Implements Dijkstra's algorithm to find the shortest path to the target
        '''
        start = (status.x, status.y)
        width, height = status.map.width, status.map.height
        distances = {start: 0}
        previous_nodes = {start: None}
        queue = [(0, start)]
        visited = set()

        while queue:
            current_distance, current_position = heapq.heappop(queue)
            if current_position in visited:
                continue
            visited.add(current_position)

            if current_position == target:
                break

            for direction in D:
                diff = direction.as_xy()
                neighbor = (current_position[0] + diff[0], current_position[1] + diff[1])
                
                if 0 <= neighbor[0] < width and 0 <= neighbor[1] < height:
                    if status.map[neighbor].status == TileStatus.Wall:
                        continue
                    
                    new_distance = current_distance + 1
                    if new_distance < distances.get(neighbor, float('inf')):
                        distances[neighbor] = new_distance
                        previous_nodes[neighbor] = (current_position, direction)
                        heapq.heappush(queue, (new_distance, neighbor))

        path = []
        step = previous_nodes.get(target)
        while step is not None:
            position, direction = step
            path.append(direction)
            step = previous_nodes.get(position)
        
        path.reverse()
        return path

    def manhattan_distance(self, start, end):
        '''
        Calculates Manhattan Distance
        '''
        return abs(start[0] - end[0]) + abs(start[1] - end[1])

    def get_possible_moves(self, status):
        '''
        Returns a list of possible moves based on current position and map status
        '''
        possible_moves = []
        for d in D:
            diff = d.as_xy()
            coord = status.x + diff[0], status.y + diff[1]
            if 0 <= coord[0] < status.map.width and 0 <= coord[1] < status.map.height:
                if status.map[coord].status != TileStatus.Wall:
                    possible_moves.append(d)
        return possible_moves

#PASS PLAYERS
players = [ScarsPathfindingPlayer()]

if __name__ == "__main__":
    pass
'''
Tasks:
Robots einsammlen
Algorithmus anschaun/verbessern
Minen - Gemeinheiten
Mauer verschieben
s -R
nächste Woche keine Stunde
in 2 Wochen 2 Robots von jedy
am 18.Juni großes Rennen
'''
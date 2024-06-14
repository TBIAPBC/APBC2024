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
class ScarsOneStepPathfinder(Player):
    '''
    This Player uses Dijkstra algorithm to find the gold 
    (but only makes one step per round). Because it is very 
    responsive it performs better than my more advanced robot.
    '''
    def reset(self, player_id, max_players, width, height):
        self.player_name = "Scar_Pathfinder_One"
        self.ourMap = Map(width, height)
        self.path = [] 

    def round_begin(self, r):
        '''
        Called at the beginning of each round
        '''
        print(f"Starting round {r}")

    def set_mines(self, status):
        '''No mine logic because it is very harmless and small'''
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

#----------------------------------------------------------------------------------------------------------------

class QuadrantGuardian(Player):
    '''
    This Robot chooses a quadrant to roost in like a hawk, based on initial position.
    It explores only that quadrant, and strikes fast when gold is in the quadrant.
    Also because it got stuck a lot it has a time-out counter (stuck_counter),
    so it has to stay put if that gets over a certain rounds.
    '''
    def reset(self, player_id, max_players, width, height):
        self.player_name = "QuadrantGuardian"
        self.ourMap = Map(width, height)
        self.path = []
        self.quadrant = None
        self.visited = set()
        self.exploration_target = None
        self.boundary_coords = None
        self.stuck_counter = 0
        self.max_stuck_rounds = 5 

    def round_begin(self, r):
        '''Called at the beginning of each round'''
        print(f"Starting round {r}")

    def set_mines(self, status):
        '''Set mines on the boundary of the quadrant when conditions are met'''
        if status.gold > 250 and not self.find_nearest_gold(status) and self.is_quadrant_more_than_80_explored():
            if not self.boundary_coords:
                self.boundary_coords = self.get_boundary_coords()
            
            # Pick a valid boundary coordinate for setting a mine
            mine_coord = self.pick_random_empty_known_boundary_coordinate(self.boundary_coords)
            
            if mine_coord:
                return [(mine_coord[0], mine_coord[1])]
        return []

    def move(self, status):
        '''
        Updates the internal map with the visible tiles, explores the quadrant,
        and moves quickly when gold is in the quadrant.
        '''
        for x in range(self.ourMap.width):
            for y in range(self.ourMap.height):
                if status.map[x, y].status != TileStatus.Unknown:
                    self.ourMap[x, y].status = status.map[x, y].status
                    self.visited.add((x, y))
    
        if not self.quadrant:
            self.quadrant = self.determine_quadrant(status)
    
        target = self.find_nearest_gold(status)
        if target:
            if not self.path or self.is_path_blocked(status):
                self.path = self.calculate_path(status, target)
                self.stuck_counter = 0  # Reset counter when path changes
            else:
                self.stuck_counter += 1  # Increment counter if path remains blocked
    
            if self.path and status.health > 30:
                max_steps = len(self.path)
                rounds_count = 1
                while True:
                    if rounds_count > 5:
                        self.stuck_counter += 1  # Increment counter if no steps taken
                        return [] if self.stuck_counter > self.max_stuck_rounds else self.explore_quadrant(status)
                    steps_this_round = round(max_steps / rounds_count)
                    path_steps_cost = ((steps_this_round * (steps_this_round + 1)) / 2) * rounds_count
                    if path_steps_cost <= 60 and status.gold >= path_steps_cost:
                        steps_to_take = steps_this_round
                        break
                    rounds_count += 1
    
                next_moves = []
                while self.path and len(next_moves) < steps_to_take:
                    next_moves.append(self.path.pop(0))
                self.stuck_counter = 0  # Reset counter when movement occurs
                return next_moves
        else:
            self.stuck_counter += 1  # Increment counter if no valid target found
            return [] if self.stuck_counter > self.max_stuck_rounds else self.explore_quadrant(status)
    
        return []  # Return an empty list if no actions are taken


    #HELPER Functions
    def is_path_blocked(self, status):
        '''
        Checks if the current path is blocked by an obstacle (another robot or a wall).
        If blocked, returns True and triggers recalculation of the path.
        '''
        if not self.path:
            return False
        
        next_move = self.path[0]
        diff = next_move.as_xy()
        next_coord = (status.x + diff[0], status.y + diff[1])
    
        if not self.is_in_quadrant(next_coord) or status.map[next_coord].status == TileStatus.Wall:
            return True
    
        return False
        
    def determine_quadrant(self, status):
        '''
        Determines the quadrant based on the initial position of the player
        '''
        mid_x = self.ourMap.width // 2
        mid_y = self.ourMap.height // 2
        if status.x < mid_x and status.y < mid_y:
            return (0, mid_x, 0, mid_y)  # Bottom-left quadrant
        elif status.x < mid_x and status.y >= mid_y:
            return (0, mid_x, mid_y, self.ourMap.height)  # Top-left quadrant
        elif status.x >= mid_x and status.y < mid_y:
            return (mid_x, self.ourMap.width, 0, mid_y)  # Bottom-right quadrant
        else:
            return (mid_x, self.ourMap.width, mid_y, self.ourMap.height)  # Top-right quadrant

    def find_nearest_gold(self, status):
        '''
        Finds the nearest gold within the quadrant (if it exists)
        '''
        if status.goldPots:
            quadrant_gold = [loc for loc in status.goldPots.keys() if self.is_in_quadrant(loc)]
            if quadrant_gold:
                return min(quadrant_gold, key=lambda loc: self.manhattan_distance((status.x, status.y), loc))
        return None

    def calculate_path(self, status, target):
        '''Implements Dijkstra's algorithm to find the shortest path to the target'''
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
                    if status.map[neighbor].status == TileStatus.Wall or not self.is_in_quadrant(neighbor):
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

    def find_next_exploration_target(self, status):
        '''Finds the nearest unexplored tile in the quadrant using a priority queue'''
        start = (status.x, status.y)
        heap = [(0, start)]  # Priority queue with distance and coordinates
        visited = set([start])
    
        while heap:
            distance, (x, y) = heapq.heappop(heap)
            if self.ourMap[x, y].status == TileStatus.Unknown and (x, y) not in self.visited:
                return (x, y)
    
            for direction in D:
                diff = direction.as_xy()
                neighbor = (x + diff[0], y + diff[1])
    
                if self.is_in_quadrant(neighbor) and neighbor not in visited:
                    visited.add(neighbor)
                    heapq.heappush(heap, (distance + 1, neighbor))
    
        return None

    def explore_quadrant(self, status):
        if not self.exploration_target or self.ourMap[self.exploration_target].status != TileStatus.Unknown:
            self.exploration_target = self.find_next_exploration_target(status)

        if self.exploration_target:
            if not self.path or (self.path and self.path[-1] != self.exploration_target):
                self.path = self.calculate_path(status, self.exploration_target)
            
            if self.is_quadrant_more_than_80_explored() or status.gold < 50 or status.health < 50:
                return []  # Rest
            elif self.path:
                return [self.path.pop(0)]
        else:
            return []

    def manhattan_distance(self, start, end):
        '''Calculates Manhattan Distance'''
        return abs(start[0] - end[0]) + abs(start[1] - end[1])

    def get_possible_moves(self, status):
        '''Returns a list of possible moves based on current position and map status'''
        possible_moves = []
        for d in D:
            diff = d.as_xy()
            coord = status.x + diff[0], status.y + diff[1]
            if 0 <= coord[0] < status.map.width and 0 <= coord[1] < status.map.height:
                if status.map[coord].status != TileStatus.Wall and self.is_in_quadrant(coord):
                    possible_moves.append(d)
        return possible_moves

    def is_in_quadrant(self, coord):
        '''Checks if a coordinate is within the chosen quadrant'''
        return self.quadrant[0] <= coord[0] < self.quadrant[1] and self.quadrant[2] <= coord[1] < self.quadrant[3]

    def is_quadrant_more_than_80_explored(self):
        '''Checks if more than 80% of the quadrant has been explored'''
        total_tiles = (self.quadrant[1] - self.quadrant[0]) * (self.quadrant[3] - self.quadrant[2])
        explored_tiles = sum(1 for x in range(self.quadrant[0], self.quadrant[1]) 
                                for y in range(self.quadrant[2], self.quadrant[3]) 
                                if self.ourMap[x, y].status != TileStatus.Unknown)
        return (explored_tiles / total_tiles) > 0.9

    def get_boundary_coords(self):
        '''Gets the boundary coordinates of the quadrant for setting mines, excluding outer map boundaries'''
        boundary_coords = []
    
        # Horizontal boundaries within the quadrant
        for x in range(self.quadrant[0], self.quadrant[1]):
            if self.quadrant[2] > 0:
                boundary_coords.append((x, self.quadrant[2] - 1))  # Bottom boundary within the quadrant
            if self.quadrant[3] < self.ourMap.height:
                boundary_coords.append((x, self.quadrant[3]))  # Top boundary within the quadrant
    
        # Vertical boundaries within the quadrant
        for y in range(self.quadrant[2], self.quadrant[3]):
            if self.quadrant[0] > 0:
                boundary_coords.append((self.quadrant[0] - 1, y))  # Left boundary within the quadrant
            if self.quadrant[1] < self.ourMap.width:
                boundary_coords.append((self.quadrant[1], y))  # Right boundary within the quadrant
    
        return boundary_coords

    def pick_random_empty_known_boundary_coordinate(self, boundary_coords):
        '''Pick a random empty known coordinate from the boundary'''
        empty_known_boundary_coords = [coord for coord in boundary_coords if self.is_valid_mine_coord(coord)]
    
        if empty_known_boundary_coords:
            return random.choice(empty_known_boundary_coords)
        else:
            return None  # If no such coordinate exists

    def is_valid_mine_coord(self, coord):
        '''Check if a coordinate is a valid position for setting a mine'''
        x, y = coord
        tile = self.ourMap[x, y]
        return tile.status != TileStatus.Unknown and tile.status != TileStatus.Wall and tile.obj is None


#PASS PLAYERS
players = [ScarsOneStepPathfinder(), QuadrantGuardian()]

if __name__ == "__main__":
    pass

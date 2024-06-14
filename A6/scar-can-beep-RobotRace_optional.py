#!/usr/bin/env python3
import random
import heapq

from game_utils import nameFromPlayerId
from game_utils import Direction as D, MoveStatus
from game_utils import Tile, TileStatus, TileObject
from game_utils import Map, Status
from simulator import Simulator
from player_base import Player

class MapGuardian(Player):
    '''
    This Player explores the entire map, targets gold pots if it's closer to them than other robots,
    and sets mines near gold pots it does not target when conditions are met.
    '''
    def reset(self, player_id, max_players, width, height):
        self.player_name = "MapGuardian"
        self.ourMap = Map(width, height)
        self.path = []
        self.visited = set()
        self.exploration_target = None
        self.boundary_coords = None
        self.other_robots_positions = {}
        self.stuck_counter = 0
        self.max_stuck_rounds = 5 

    def round_begin(self, r):
        '''Called at the beginning of each round'''
        print(f"Starting round {r}")

    def set_mines(self, status):
        '''Set mines near gold pots when conditions are met'''
        if status.gold > 250 and not self.find_nearest_gold(status) and self.is_more_than_80_explored():
            if not self.boundary_coords:
                self.boundary_coords = self.get_boundary_coords()
            
            # Pick a valid boundary coordinate for setting a mine
            mine_coord = self.pick_random_empty_known_boundary_coordinate(self.boundary_coords)
            
            if mine_coord:
                return [(mine_coord[0], mine_coord[1])]
            
        return []

    def move(self, status):
        '''
        Updates the internal map with the visible tiles, explores the map,
        and moves towards gold pots or explores as needed.
        '''
        # Update the internal map with visible tiles
        for x in range(self.ourMap.width):
            for y in range(self.ourMap.height):
                if status.map[x, y].status != TileStatus.Unknown:
                    self.ourMap[x, y].status = status.map[x, y].status
                    self.visited.add((x, y))
    
        self.update_other_robots_positions(status)
    
        # Find the nearest gold based on the known map
        target = self.find_nearest_gold(status)
        if target:
            # Calculate or update path to the nearest gold
            if not self.path or self.is_path_blocked(status):
                self.path = self.calculate_path(status, target)
                self.stuck_counter = 0  # Reset counter when path changes
                print('MapG changed path!')
            else:
                self.stuck_counter += 1  # Increment counter if path remains blocked
    
            if self.path and status.health > 30:
                max_steps = len(self.path)
                rounds_count = 1
                while True:
                    if rounds_count > 5:
                        self.stuck_counter += 1  # Increment counter if no steps taken
                        return [] if self.stuck_counter > self.max_stuck_rounds else self.explore_map(status)
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
            return [] if self.stuck_counter > self.max_stuck_rounds else self.explore_map(status)
    
        return []  # Return an empty list if no actions are taken
    
    def explore_map(self, status):
        '''
        Explores the map by finding unexplored tiles.
        '''
        if not self.exploration_target or self.ourMap[self.exploration_target].status != TileStatus.Unknown:
            self.exploration_target = self.find_next_exploration_target(status)
    
        if self.exploration_target:
            if not self.path or (self.path and self.path[-1] != self.exploration_target):
                self.path = self.calculate_path(status, self.exploration_target)
    
            # Adjust exploration conditions based on game state
            if self.is_more_than_80_explored() or status.gold < 50 or status.health < 50:
                return []  # Rest
            elif self.path:
                return [self.path.pop(0)]
    
        return []

    
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
    
        # Check if next move is within map boundaries
        if not (0 <= next_coord[0] < self.ourMap.width and 0 <= next_coord[1] < self.ourMap.height):
            return True
    
        # Check if next move is into a wall
        if status.map[next_coord].status == TileStatus.Wall:
            return True
    
        # Check if next move is into another robot's position
        #if next_coord in self.other_robots_positions:
        #    return True
    
        return False


    def update_other_robots_positions(self, status):
        '''Updates the positions of other robots based on the visible map'''
        self.other_robots_positions = {}
        for x in range(self.ourMap.width):
            for y in range(self.ourMap.height):
                tile = self.ourMap[x, y]
                if tile.obj and tile.obj != TileObject.Gold:
                    self.other_robots_positions[(x, y)] = tile.obj

    def find_nearest_gold(self, status, max_step_size=8):
        '''
        Finds the nearest gold pot that is closer to this player than any visible robots,
        and within a maximum step size.
        '''
        if status.goldPots:
            nearest_gold = None
            min_distance = float('inf')
            for loc in status.goldPots.keys():
                if self.is_within_step_size(loc, status, max_step_size):
                    distance = self.manhattan_distance((status.x, status.y), loc)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_gold = loc
            return nearest_gold
        return None


    def is_closer_than_visible_robots(self, loc, status):
        '''Checks if this player is closer to the given location than any visible robot'''
        our_distance = self.manhattan_distance((status.x, status.y), loc)
        for robot_pos in self.other_robots_positions.keys():
            robot_distance = self.manhattan_distance(robot_pos, loc)
            if robot_distance <= our_distance:
                return False
        return True
        
    def is_within_step_size(self, loc, status, max_step_size):
        '''Checks if the distance to the location is within the specified step size'''
        distance = self.manhattan_distance((status.x, status.y), loc)
        return distance <= max_step_size


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

    def find_next_exploration_target(self, status):
        '''Finds the nearest unexplored tile using a priority queue'''
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
    
                if 0 <= neighbor[0] < self.ourMap.width and 0 <= neighbor[1] < self.ourMap.height:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        heapq.heappush(heap, (distance + 1, neighbor))
    
        return None


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
                if status.map[coord].status != TileStatus.Wall:
                    possible_moves.append(d)
        return possible_moves

    def is_more_than_80_explored(self):
        '''Checks if more than 80% of the map has been explored'''
        total_tiles = self.ourMap.width * self.ourMap.height
        explored_tiles = sum(1 for x in range(self.ourMap.width) 
                                for y in range(self.ourMap.height) 
                                if self.ourMap[x, y].status != TileStatus.Unknown)
        return (explored_tiles / total_tiles) > 0.8

    def get_boundary_coords(self):
        '''Gets the boundary coordinates near gold pots for setting mines, excluding outer map boundaries'''
        boundary_coords = []
    
        for gold in self.ourMap.goldPots:
            for direction in D:
                diff = direction.as_xy()
                neighbor = (gold[0] + diff[0], gold[1] + diff[1])
                if 0 <= neighbor[0] < self.ourMap.width and 0 <= neighbor[1] < self.ourMap.height:
                    boundary_coords.append(neighbor)
    
        return boundary_coords

        
    def pick_random_empty_known_boundary_coordinate(self, boundary_coords):
        '''Picks a random empty and known coordinate from the boundary coordinates'''
        empty_known_boundary_coords = []
        for coord in boundary_coords:
            x, y = coord
            tile = self.ourMap[x, y]
            if tile.status != TileStatus.Unknown and tile.status != TileStatus.Wall and tile.obj is None:
                empty_known_boundary_coords.append((x, y))
    
        if empty_known_boundary_coords:
            return random.choice(empty_known_boundary_coords)
        else:
            return None

players = [MapGuardian()]
if __name__ == "__main__":
    pass

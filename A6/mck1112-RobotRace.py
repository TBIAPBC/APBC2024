import heapq
import random
from game_utils import Direction as D, TileStatus, Map
from player_base import Player

# Implementation of the A* path-finding algorithm
class PathfindingNode:
    def __init__(self, position, parent=None, g_cost=0, h_cost=0):
        self.position = position
        self.parent_node = parent
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f_cost < other.f_cost

def heuristic(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def a_star_search(start, goal, our_map):
    start_node = PathfindingNode(start, None, 0, heuristic(start, goal))
    open_list = [start_node]
    closed_list = set()

    while open_list:
        current_node = heapq.heappop(open_list)

        if current_node.position == goal:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent_node
            return path[::-1]

        closed_list.add(current_node.position)

        for direction in D:
            neighbor_pos = (current_node.position[0] + direction.as_xy()[0],
                            current_node.position[1] + direction.as_xy()[1])

            if (neighbor_pos[0] < 0 or neighbor_pos[0] >= our_map.width or
                    neighbor_pos[1] < 0 or neighbor_pos[1] >= our_map.height):
                continue

            neighbor_tile = our_map[neighbor_pos[0], neighbor_pos[1]]
            if neighbor_tile.status == TileStatus.Wall:
                continue

            neighbor_node = PathfindingNode(neighbor_pos, current_node,
                                            current_node.g_cost + 1, heuristic(neighbor_pos, goal))

            if neighbor_pos in closed_list:
                continue

            open_node = next((node for node in open_list if node == neighbor_node), None)
            if open_node is not None and open_node.g_cost <= neighbor_node.g_cost:
                continue

            heapq.heappush(open_list, neighbor_node)

    return []

class Smarty(Player):
    def __init__(self):
        super().__init__()
        self.player_name = "Smarty"
        self.our_map = Map(10, 10)  # Assuming initial map size is 10x10
        self.visited = [[0] * 10 for _ in range(10)]  # Assuming initial map size is 10x10
        self.goal = None

    def reset(self, player_id, max_players, width, height, rules=None):
        self.our_map = Map(width, height)
        self.visited = [[0] * width for _ in range(height)]
        self.rules = rules
        self.goal = None

    def round_begin(self, r):
        self.goal = None

    def _update_map(self, status):
        for x in range(self.our_map.width):
            for y in range(self.our_map.height):
                if status.map[x, y].status != TileStatus.Unknown:
                    self.our_map[x, y].status = status.map[x, y].status

    def _as_direction(self, curpos, nextpos):
        for d in D:
            diff = d.as_xy()
            if (curpos[0] + diff[0], curpos[1] + diff[1]) == nextpos:
                return d
        return None

    def _get_path_to_goal(self, start, goal):
        return a_star_search(start, goal, self.our_map)

    def _find_best_gold_pot(self, status):
        current_pos = (status.x, status.y)
        best_gold = None
        min_cost = float('inf')

        for gLoc in status.goldPots.keys():
            path = self._get_path_to_goal(current_pos, gLoc)
            if not path:
                continue

            cost = len(path) + heuristic(current_pos, gLoc) / status.goldPots[gLoc]
            if cost < min_cost:
                min_cost = cost
                best_gold = gLoc

        return best_gold

    def move(self, status):
        self._update_map(status)
        current_pos = (status.x, status.y)

        if not status.goldPots:
            return [random.choice(list(D))]  # Move randomly if no gold is present

        if self.goal is None or self.goal not in status.goldPots:
            self.goal = self._find_best_gold_pot(status)
        
        if self.goal is None:
            return [random.choice(list(D))]  # Move randomly if no gold is found

        path = self._get_path_to_goal(current_pos, self.goal)
        if not path:
            self.goal = None
            return [random.choice(list(D))]  # Move randomly if no path is found

        next_move = path[1] if len(path) > 1 else path[0]
        direction = self._as_direction(current_pos, next_move)
        
        return [direction] if direction else [random.choice(list(D))]

players = [Smarty()]





# result 
# Player   Health   Gold      Position
# smarty   100      1836      10,11
# test-1   100      1340      10,12
# test-2   35       2         29,29
# beatme   100      2542      27,12

# not that efficient as we wanted it to be
# needs to be improved not that smart yet
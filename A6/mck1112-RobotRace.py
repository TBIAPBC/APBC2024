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

def a_star_search(start, goal, our_map, avoid_positions=set()):
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
            if neighbor_tile.status == TileStatus.Wall or neighbor_pos in avoid_positions:
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

class ImprovedSmarty(Player):
    def __init__(self):
        super().__init__()
        self.player_name = "ImprovedSmarty"
        self.our_map = Map(10, 10)
        self.visited = [[0] * 10 for _ in range(10)]
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

    def _get_path_to_goal(self, start, goal, avoid_positions=set()):
        if goal is None:
            return []  # If the goal is not set, return an empty path
        return a_star_search(start, goal, self.our_map, avoid_positions)

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

    def _explore(self, current_pos):
        unexplored = []
        for x in range(self.our_map.width):
            for y in range(self.our_map.height):
                if self.our_map[x, y].status == TileStatus.Unknown and self.visited[x][y] == 0:
                    unexplored.append((x, y))
        if unexplored:
            nearest_unexplored = min(unexplored, key=lambda pos: heuristic(current_pos, pos))
            path = self._get_path_to_goal(current_pos, nearest_unexplored)
            if path and len(path) > 1:
                return self._as_direction(current_pos, path[1])

        directions = list(D)
        random.shuffle(directions)
        for d in directions:
            new_pos = (current_pos[0] + d.as_xy()[0], current_pos[1] + d.as_xy()[1])
            if (0 <= new_pos[0] < self.our_map.width and 0 <= new_pos[1] < self.our_map.height and 
                self.our_map[new_pos[0], new_pos[1]].status != TileStatus.Wall and 
                self.visited[new_pos[0]][new_pos[1]] == 0):
                return d
        return random.choice(directions)

    def set_mines(self, status):
        mine_positions = []
        current_pos = (status.x, status.y)
        if self.goal is None:
            return mine_positions  # If the goal is None, do not set any mines

        for x in range(current_pos[0] - 3, current_pos[0] + 3):
            for y in range(current_pos[1] - 3, current_pos[1] + 3):
                if 0 <= x < self.our_map.width and 0 <= y < self.our_map.height:
                    if status.map[x, y].obj and status.map[x, y].obj.is_player():
                        path = self._get_path_to_goal((x, y), self.goal)
                        if path:
                            mine_positions.extend(path[:3])  # Place mines on the first three steps of the path
        return mine_positions

    def move(self, status):
        self._update_map(status)
        current_pos = (status.x, status.y)
        self.visited[current_pos[0]][current_pos[1]] += 1

        if not status.goldPots:
            return [self._explore(current_pos)]

        if self.goal is None or self.goal not in status.goldPots:
            self.goal = self._find_best_gold_pot(status)

        if self.goal is None:
            return [self._explore(current_pos)]

        avoid_positions = set((p.x, p.y) for p in status.others if p)
        path = self._get_path_to_goal(current_pos, self.goal, avoid_positions)

        if not path:
            self.goal = None
            return [self._explore(current_pos)]

        next_move = path[1] if len(path) > 1 else path[0]
        direction = self._as_direction(current_pos, next_move)

        return [direction] if direction else [self._explore(current_pos)]

players = [ImprovedSmarty()]

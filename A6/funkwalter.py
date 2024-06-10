import heapq
import numpy as np
from game_utils import Direction as D, TileStatus, Map
from player_base import Player

class funkwalter(Player):

    def __init__(self, *, random=True):
        self.random = random

    def reset(self, player_id, max_players, width, height):
        self.player_name = "funkWalter"
        self.ourMap = Map(width, height)
        self.visited = set()
        self.exploring = True
        self.round_counter = 0
        self.gold_pot_reset_round = 0
        self.last_gold_pot_location = None
        self.player_id = player_id

    def round_begin(self, r):
        self.round_counter = r

    def _as_direction(self, curpos, nextpos):
        for d in D:
            diff = d.as_xy()
            if (curpos[0] + diff[0], curpos[1] + diff[1]) == nextpos:
                return d
        return None

    def _as_directions(self, curpos, path):
        return [self._as_direction(x, y) for x, y in zip([curpos] + path, path)]

    def _is_within_bounds(self, pos):
        x, y = pos
        return 0 <= x < self.ourMap.width and 0 <= y < self.ourMap.height

    def _explore(self, curpos, numMoves):
        moves = []
        for _ in range(numMoves):
            neighbors = []
            for d in D:
                diff = d.as_xy()
                new_pos = curpos[0] + diff[0], curpos[1] + diff[1]

                if self._is_within_bounds(new_pos) and new_pos not in self.visited:
                    tile = self.ourMap[new_pos[0], new_pos[1]]
                    if tile.status == TileStatus.Unknown or tile.status == TileStatus.Empty:
                        neighbors.append((d, new_pos))
            if not neighbors:
                break

            move = neighbors[0][0]
            if move:
                moves.append(move)
                diff = move.as_xy()
                curpos = curpos[0] + diff[0], curpos[1] + diff[1]
                self.visited.add(curpos)
        return moves

    def dijkstra(self, start, goal):
        width, height = self.ourMap.width, self.ourMap.height
        dist = np.full((width, height), np.inf)
        dist[start] = 0
        priority_queue = [(0, start)]
        heapq.heapify(priority_queue)
        came_from = {}

        while priority_queue:
            current_dist, current = heapq.heappop(priority_queue)

            if current == goal:
                break

            for d in D:
                diff = d.as_xy()
                neighbor = (current[0] + diff[0], current[1] + diff[1])

                if self._is_within_bounds(neighbor) and self.ourMap[neighbor].status != TileStatus.Wall:
                    new_dist = current_dist + 1  # All moves cost the same (1)
                    if new_dist < dist[neighbor]:
                        dist[neighbor] = new_dist
                        heapq.heappush(priority_queue, (new_dist, neighbor))
                        came_from[neighbor] = current

        # Reconstruct path
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from.get(current, start)
        path.reverse()
        return path

    def move(self, status):
        ourMap = self.ourMap
        for x in range(ourMap.width):
            for y in range(ourMap.height):
                if status.map[x, y].status != TileStatus.Unknown:
                    ourMap[x, y].status = status.map[x, y].status
                    self.visited.add((x, y))

        curpos = (status.x, status.y)

        assert len(status.goldPots) > 0
        gLoc = next(iter(status.goldPots))

        if self.last_gold_pot_location and gLoc != self.last_gold_pot_location:
            self.gold_pot_reset_round = self.round_counter

        self.last_gold_pot_location = gLoc

        bestpath = self.dijkstra(curpos, gLoc)
        distance = len(bestpath)

        numMoves = min(4, distance)  # Dynamic adjustment based on distance

        goldPotRemainingRounds = status.goldPotRemainingRounds
        if distance > goldPotRemainingRounds:
            numMoves = 0  # Avoid moving if gold pot is out of reach

        if status.gold < numMoves * (numMoves + 1) / 2:
            numMoves = 0  # Avoid moving if not enough gold to cover the cost of moves

        # Check proximity of other players and mines based on visible characters
        avoid_move = False
        for x in range(max(0, gLoc[0] - 4), min(gLoc[0] + 5, ourMap.width)):
            for y in range(max(0, gLoc[1] - 4), min(gLoc[1] + 5, ourMap.height)):
                tile_status = status.map[x, y].status
                if tile_status == '&':
                    # Avoid moving into a mine
                    avoid_move = True
                    break
                elif tile_status not in (TileStatus.Unknown, TileStatus.Wall, TileStatus.Empty, '&'):
                    # Found another player
                    robot_distance = len(self.dijkstra((x, y), gLoc))
                    if robot_distance <= 4 and distance > 4:
                        avoid_move = True
                        break
            if avoid_move:
                break

        if avoid_move:
            numMoves = 0

        moves = self._explore(curpos, numMoves)
        if not moves:
            moves = self._as_directions(curpos, bestpath[:numMoves])
        return moves

players = [funkwalter()]


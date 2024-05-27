from player_base import Player
from game_utils import Direction as D, TileStatus, TileObject, Map
from shortestpaths import AllShortestPaths
import random


class funkwalter(Player):
    def __init__(self, *, random=True):
        self.random = random
        self.goldPotRemainingRounds = None
        self.known_positions = {}

    def reset(self, player_id, max_players, width, height):
        self.player_name = "funkwalter"
        self.player_id = player_id  # Store player_id here
        self.width = width
        self.height = height
        self.ourMap = Map(width, height)
        self.goldPotRemainingRounds = None
        self.known_positions.clear()

    def round_begin(self, r):
        # Reset or update state variables at the beginning of each round
        pass

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
        return 0 <= x < self.width and 0 <= y < self.height

    def _avoid_mines_and_robots(self, path):
        # Implement logic to avoid mines and other robots
        safe_path = []
        for pos in path:
            if self.ourMap[pos].status != TileStatus.Mine and pos not in self.known_positions.values():
                safe_path.append(pos)
        return safe_path

    def _explore_unknown(self, curpos):
        # Implement logic to explore unknown areas
        directions = list(D)
        random.shuffle(directions)
        for d in directions:
            new_pos = (curpos[0] + d.as_xy()[0], curpos[1] + d.as_xy()[1])
            if self._is_within_bounds(new_pos) and self.ourMap[new_pos].status == TileStatus.Unknown:
                return [new_pos]
        return []

    def move(self, status):
        ourMap = self.ourMap
        for x in range(ourMap.width):
            for y in range(ourMap.height):
                if status.map[x, y].status != TileStatus.Unknown:
                    ourMap[x, y].status = status.map[x, y].status

        curpos = (status.x, status.y)
        self.known_positions[self.player_id] = curpos  # Store position of this robot

        assert len(status.goldPots) > 0
        gLoc = next(iter(status.goldPots))
        self.goldPotRemainingRounds = status.goldPotRemainingRounds

        paths = AllShortestPaths(gLoc, ourMap)
        if self.random:
            bestpath = paths.randomShortestPathFrom(curpos)
        else:
            bestpath = paths.shortestPathFrom(curpos)

        bestpath = bestpath[1:]  # remove the current position
        bestpath.append(gLoc)

        bestpath = self._avoid_mines_and_robots(bestpath)
        if not bestpath:
            bestpath = self._explore_unknown(curpos)

        distance = len(bestpath)

        # Dynamic halfway distance check based on remaining rounds and map dimensions
        half_map_distance = min(self.width, self.height) / 2
        if distance > self.goldPotRemainingRounds or distance > half_map_distance:
            # Explore if not moving towards the gold pot
            exploration_path = self._explore_unknown(curpos)
            if exploration_path:
                return self._as_directions(curpos, exploration_path)
            return []  # Stay put if there's no unknown area to explore

        # Move towards the gold pot
        return self._as_directions(curpos, bestpath)


players = [funkwalter()]


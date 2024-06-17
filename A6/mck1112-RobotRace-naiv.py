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
        self.player_name = "mck1112 NaivePlayer"
        self.moves = [D.up, D.left, D.down, D.right, D.up_left, D.down_left, D.down_right, D.up_right]
        self.visited = set()
        self.max_width = width
        self.max_height = height

    def round_begin(self, r):
        pass

    def set_mines(self, status):
        return []

    def move(self, status):
        self.visited.add((status.x, status.y))
        random.shuffle(self.moves)
        
        for direction in self.moves:
            dx, dy = direction.as_xy()
            new_x, new_y = status.x + dx, status.y + dy
            
            if 0 <= new_x < self.max_width and 0 <= new_y < self.max_height:
                if not status.map[new_x, new_y].is_blocked() and (new_x, new_y) not in self.visited:
                    return [direction]
        
        for direction in self.moves:
            dx, dy = direction.as_xy()
            new_x, new_y = status.x + dx, status.y + dy
            
            if 0 <= new_x < self.max_width and 0 <= new_y < self.max_height:
                if not status.map[new_x, new_y].is_blocked():
                    return [direction]
        
        return [D.stay]

players = [NaivePlayer()]


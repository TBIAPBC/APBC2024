#!/usr/bin/env python3

from game_utils import Direction as D
from game_utils import TileStatus
from game_utils import Map
from player_base import Player
import pickle

from shortestpaths import AllShortestPaths

class Llewi0(Player):

        def __init__(self,*,random=True):
                self.random=random

        def reset(self, player_id, max_players, width, height):
                self.player_name = "Llewi0"
                self.ourMap = Map(width, height)
                self.vision = 5

        def round_begin(self, r):
                pass

        def _as_direction(self,curpos,nextpos):
                for d in D:
                        diff = d.as_xy()
                        if (curpos[0] + diff[0], curpos[1] + diff[1]) ==  nextpos:
                                return d
                return None

        def _as_directions(self,curpos,path):
                return [self._as_direction(x,y) for x,y in zip([curpos]+path,path) if self._as_direction(x,y)]

        def _find_unvisited_field(self):
                # Create candidates
                ourMap = self.ourMap
                width = ourMap.width
                height = ourMap.height
                vision = self.vision

                # Start near corners
                offset = 2
                
                # Candidates go from outermost corners to corners further in
                nodes = []
                while True:
                    new_nodes = [(offset, offset), (offset, height-offset), (width-offset, height-offset), (width-offset, offset)]
                    nodes = [*nodes, *new_nodes]
                    offset += vision
                    if offset >= width//2 or offset >= height//2:
                           break
                
                # Find first that is unvisited
                for node in nodes:
                       if ourMap[node].status == TileStatus.Unknown:
                              return node
                return None

        def move(self, status):
                
                # Update our map
                ourMap = self.ourMap
                for x in range(ourMap.width):
                        for y in range(ourMap.height):
                                if status.map[x, y].status != TileStatus.Unknown:
                                        ourMap[x, y].status = status.map[x, y].status
                
                print("MY VISION")
                print(ourMap)
                
                # Find shortest path to gold
                shortest_gold = None
                for goldPot in status.goldPots:
                       paths = AllShortestPaths(goldPot, ourMap)
                       path = paths.randomShortestPathFrom((status.x, status.y))
                       path.append(goldPot)
                       if (shortest_gold is None) or (len(path) < len(shortest_gold)):
                              shortest_gold = path
                
                # If it's in vision range always go
                if (shortest_gold is not None) and len(shortest_gold) < self.vision:
                       retval = self._as_directions((status.x,status.y), shortest_gold)
                       #print(f"0 {retval}")
                       return retval

                # Otherwise check out map
                target = self._find_unvisited_field()
                if target:
                       paths = AllShortestPaths(target, ourMap)
                       path = paths.randomShortestPathFrom((status.x, status.y))
                       retval = self._as_directions((status.x,status.y), path)[:3]
                       #print(f"1 {retval}")
                       return retval
                
                # Map has been explored, go for gold
                if len(shortest_gold) > 10:
                       shortest_gold = shortest_gold[:10]
                retval = self._as_directions((status.x,status.y), shortest_gold)
                #print(f"2 {retval}")
                return retval

        def moveOld(self, status):
                # print("-" * 80)
                print("Status for %s" % self.player_name)
                print(status)
                print("that was the status")

                ourMap = self.ourMap
                #print("Our Map, before")
                #print(ourMap)
                for x in range(ourMap.width):
                        for y in range(ourMap.height):
                                if status.map[x, y].status != TileStatus.Unknown:
                                        ourMap[x, y].status = status.map[x, y].status
                print("Our Map, after")
                print(ourMap)
                print("that was our map")

                curpos = (status.x,status.y)

                assert len(status.goldPots) > 0
                gLoc = next(iter(status.goldPots))

                print("gLoc")
                print(gLoc)

                ## determine next move d based on shortest path finding
                paths = AllShortestPaths(gLoc,ourMap)

                #print("paths")
                #print(next(iter(paths)))

                with open("self.pkl", "wb") as f:
                    pickle.dump(self, f)
                with open("status.pkl", "wb") as f:
                    pickle.dump(status, f)

                if self.random:
                        bestpath = paths.randomShortestPathFrom(curpos)
                else:
                        bestpath = paths.shortestPathFrom(curpos)

                bestpath = bestpath[1:]
                bestpath.append( gLoc )

                distance=len(bestpath)

                numMoves = 1

                ## don't move if the pot is too far away
                if numMoves>0 and distance/numMoves > status.goldPotRemainingRounds:
                        numMoves = 0
                        # print("SillyScout: I rather wait")

                return self._as_directions(curpos,bestpath[:numMoves])

players = [ Llewi0()]

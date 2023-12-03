import copy
import math
import queue
import random
import select
import sys
import time


class Bot:
    def __init__(self, W):
        # Bot knows the width of the maze  
        self.W = W
        self.goalTile = self.W - 1
        
        # current exact position
        self.tile_x = 0.5
        self.tile_y = 0.5

        # last tile "reached" (i.e., being close enough to center)
        self.tile_x = 0
        self.tile_y = 0

        self.pathcost = 0
        
        self.seen = set()
        self.dead = set()
        self.walls = set()
        self.paths = []
        
        for i in range(0, 11):
            self.walls |= {(i, 0, i + 1, 0), (i, 11, i + 1, 11), (0, i, 0, i + 1), (11, i, 11, i + 1)}

        # We keep a list of valid moves to backtrack
        self.moves = []
        self.returnMoves = []

        self.minPath = []
        self.minPathIndx = 0
        self.searching = True

    def current_tile(self):
        return (self.tile_x, self.tile_y)

    def goal(self):
        return self.tile_x == self.goalTile and self.tile_y == self.goalTile

    def changeGoal(self):
        if self.goalTile == self.W - 1: 
            self.goalTile = 0
        else:
            self.goalTile = self.W - 1

        return

    # Clear all the paths including seen walls
    def cacheMoves(self):
        moves = copy.deepcopy(self.moves)
        self.returnMoves = moves
        self.paths.append([moves, self.pathcost, self.goalTile])
        print(f"comment added path to self.path: {self.moves}")
        print(f"comment self.paths: {self.paths}")
        self.pathcost = 0
        self.moves.clear()
        self.seen.clear()
        print(f"comment self.paths after clear: {self.paths}")

        return

    def step(self, new_tile):
        # if new_tile in bot.moves:
        #   print(f"comment seen tile: {new_tile}")
        #   print(f"comment moves: {bot.moves}")
        #   tile_index = bot.moves.index(new_tile)
        #   print(f"comment tile index: {tile_index}")
        #   path_cost_diff = len(bot.moves) - 1 - tile_index
        #   print(f"comment number of moves: {len(bot.moves)}")
        #   print(f"comment bot path cost: {bot.pathcost}")
        #   print(f"comment path cost diff: {path_cost_diff}")
        #   bot.pathcost -= path_cost_diff
        #   print(f"comment updated path cost: {bot.pathcost}")
        #   bot.moves = bot.moves[:tile_index+1]
        #   print(f"comment updated bot moves: {bot.moves}")
        self.tile_x = new_tile[0]
        self.tile_y = new_tile[1]
        self.pathcost += 1

    def checkMove(self, dir):
        assert dir in ["R", "L", "U", "D", "RD", "RU", "LD", "LU"], "Invalid direction given"

        if dir == "D":
            # (self.tile_x, self.tile_y + 1) not in self.dead|self.seen and (self.tile_x, self.tile_y + 1, self.tile_x + 1, self.tile_y + 1) not in self.walls
            x = self.tile_x
            y = self.tile_y + 1
            wall_x1 = self.tile_x
            wall_y1 = self.tile_y + 1
            wall_x2 = self.tile_x + 1
            wall_y2 = self.tile_y + 1

        elif dir == "R":
            # (self.tile_x + 1, self.tile_y) not in self.dead|self.seen and (self.tile_x + 1, self.tile_y, self.tile_x + 1, self.tile_y + 1) not in self.walls
            x = self.tile_x + 1
            y = self.tile_y 
            wall_x1 = self.tile_x + 1
            wall_y1 = self.tile_y 
            wall_x2 = self.tile_x + 1
            wall_y2 = self.tile_y + 1
        elif dir == "L":
            # (self.tile_x - 1, self.tile_y) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x, self.tile_y + 1) not in self.walls
            x = self.tile_x - 1
            y = self.tile_y 
            wall_x1 = self.tile_x
            wall_y1 = self.tile_y 
            wall_x2 = self.tile_x 
            wall_y2 = self.tile_y + 1
        else:
            # (self.tile_x, self.tile_y - 1) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x + 1, self.tile_y) not in self.walls
            x = self.tile_x 
            y = self.tile_y -1 
            wall_x1 = self.tile_x
            wall_y1 = self.tile_y 
            wall_x2 = self.tile_x + 1
            wall_y2 = self.tile_y    
            
        return (x, y) not in self.dead|self.seen and (wall_x1, wall_y1, wall_x2, wall_y2) not in self.walls


    def actions(self):
        actions = []
        # MOVEMENT
        rand = random.uniform(0, 1)
        if self.goalTile == self.W - 1:
            if rand < 0.5:
                # Move Down
                if self.checkMove("D"):
                    actions.append((self.tile_x, self.tile_y + 1))
                # Move Right
                if self.checkMove("R"):
                    actions.append((self.tile_x + 1, self.tile_y))
                # Move Left
                if self.checkMove("L"):
                    actions.append((self.tile_x - 1, self.tile_y))
                # Move Up
                if self.checkMove("U"):
                    actions.append((self.tile_x, self.tile_y - 1))
                if((self.tile_x+1, self.tile_y+1) not in self.dead|self.seen and (self.tile_x, self.tile_y+1, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y+1, self.tile_x+2, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y+1, self.tile_x+1, self.tile_y+2) not in self.walls):
                  actions.append((self.tile_x+1, self.tile_y+1)) # diagonal right down
                if((self.tile_x+1, self.tile_y-1) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x+1, self.tile_y) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+2, self.tile_y) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y-1, self.tile_x+1, self.tile_y) not in self.walls):
                  actions.append((self.tile_x+1, self.tile_y-1)) # diagonal right up
                if((self.tile_x-1, self.tile_y+1) not in self.dead|self.seen and (self.tile_x, self.tile_y+1, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x-1, self.tile_y+1, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y+1, self.tile_x, self.tile_y+2) not in self.walls):
                  actions.append((self.tile_x-1, self.tile_y+1)) # diagonal left down
                if((self.tile_x-1, self.tile_y-1) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x+1, self.tile_y) not in self.walls and (self.tile_x-1, self.tile_y, self.tile_x, self.tile_y) not in self.walls and (self.tile_x, self.tile_y, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y-1, self.tile_x, self.tile_y) not in self.walls):
                  actions.append((self.tile_x-1, self.tile_y-1))# diagonal left up
                
            else:
                # Move Right
                if self.checkMove("R"):
                    actions.append((self.tile_x + 1, self.tile_y))
                # Move Down
                if self.checkMove("D"):
                    actions.append((self.tile_x, self.tile_y + 1))
                # Move Up
                if self.checkMove("U"):
                    actions.append((self.tile_x, self.tile_y - 1))
                # Move Left
                if self.checkMove("L"):
                    actions.append((self.tile_x - 1, self.tile_y))
                if((self.tile_x+1, self.tile_y+1) not in self.dead|self.seen and (self.tile_x, self.tile_y+1, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y+1, self.tile_x+2, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y+1, self.tile_x+1, self.tile_y+2) not in self.walls):
                  actions.append((self.tile_x+1, self.tile_y+1)) # diagonal right down
                if((self.tile_x+1, self.tile_y-1) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x+1, self.tile_y) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+2, self.tile_y) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y-1, self.tile_x+1, self.tile_y) not in self.walls):
                  actions.append((self.tile_x+1, self.tile_y-1)) # diagonal right up
                if((self.tile_x-1, self.tile_y+1) not in self.dead|self.seen and (self.tile_x, self.tile_y+1, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x-1, self.tile_y+1, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y+1, self.tile_x, self.tile_y+2) not in self.walls):
                  actions.append((self.tile_x-1, self.tile_y+1)) # diagonal left down
                if((self.tile_x-1, self.tile_y-1) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x+1, self.tile_y) not in self.walls and (self.tile_x-1, self.tile_y, self.tile_x, self.tile_y) not in self.walls and (self.tile_x, self.tile_y, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y-1, self.tile_x, self.tile_y) not in self.walls):
                  actions.append((self.tile_x-1, self.tile_y-1))# diagonal left up
        else:
            if rand < 0.5:
                # Move Up
                if self.checkMove("U"):
                    actions.append((self.tile_x, self.tile_y - 1))
                # Move Left
                if self.checkMove("L"):
                    actions.append((self.tile_x - 1, self.tile_y))
                # Move Right
                if self.checkMove("R"):
                    actions.append((self.tile_x + 1, self.tile_y))
                # Move Down
                if self.checkMove("D"):
                    actions.append((self.tile_x, self.tile_y + 1))
                if((self.tile_x+1, self.tile_y+1) not in self.dead|self.seen and (self.tile_x, self.tile_y+1, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y+1, self.tile_x+2, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y+1, self.tile_x+1, self.tile_y+2) not in self.walls):
                  actions.append((self.tile_x+1, self.tile_y+1)) # diagonal right down
                if((self.tile_x+1, self.tile_y-1) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x+1, self.tile_y) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+2, self.tile_y) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y-1, self.tile_x+1, self.tile_y) not in self.walls):
                  actions.append((self.tile_x+1, self.tile_y-1)) # diagonal right up
                if((self.tile_x-1, self.tile_y+1) not in self.dead|self.seen and (self.tile_x, self.tile_y+1, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x-1, self.tile_y+1, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y+1, self.tile_x, self.tile_y+2) not in self.walls):
                  actions.append((self.tile_x-1, self.tile_y+1)) # diagonal left down
                if((self.tile_x-1, self.tile_y-1) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x+1, self.tile_y) not in self.walls and (self.tile_x-1, self.tile_y, self.tile_x, self.tile_y) not in self.walls and (self.tile_x, self.tile_y, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y-1, self.tile_x, self.tile_y) not in self.walls):
                  actions.append((self.tile_x-1, self.tile_y-1))# diagonal left up
                
            else:
                # Move Left
                if self.checkMove("L"):
                    actions.append((self.tile_x - 1, self.tile_y))
                # Move Up
                if self.checkMove("U"):
                    actions.append((self.tile_x, self.tile_y - 1))
                # Move Down
                if self.checkMove("D"):
                    actions.append((self.tile_x, self.tile_y + 1))
                # Move Right
                if self.checkMove("R"):
                    actions.append((self.tile_x + 1, self.tile_y))
                if((self.tile_x+1, self.tile_y+1) not in self.dead|self.seen and (self.tile_x, self.tile_y+1, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y+1, self.tile_x+2, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y+1, self.tile_x+1, self.tile_y+2) not in self.walls):
                  actions.append((self.tile_x+1, self.tile_y+1)) # diagonal right down
                if((self.tile_x+1, self.tile_y-1) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x+1, self.tile_y) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+2, self.tile_y) not in self.walls and (self.tile_x+1, self.tile_y, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x+1, self.tile_y-1, self.tile_x+1, self.tile_y) not in self.walls):
                  actions.append((self.tile_x+1, self.tile_y-1)) # diagonal right up
                if((self.tile_x-1, self.tile_y+1) not in self.dead|self.seen and (self.tile_x, self.tile_y+1, self.tile_x+1, self.tile_y+1) not in self.walls and (self.tile_x-1, self.tile_y+1, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y+1, self.tile_x, self.tile_y+2) not in self.walls):
                  actions.append((self.tile_x-1, self.tile_y+1)) # diagonal left down
                if((self.tile_x-1, self.tile_y-1) not in self.dead|self.seen and (self.tile_x, self.tile_y, self.tile_x+1, self.tile_y) not in self.walls and (self.tile_x-1, self.tile_y, self.tile_x, self.tile_y) not in self.walls and (self.tile_x, self.tile_y, self.tile_x, self.tile_y+1) not in self.walls and (self.tile_x, self.tile_y-1, self.tile_x, self.tile_y) not in self.walls):
                  actions.append((self.tile_x-1, self.tile_y-1))# diagonal left up
                
                
        if len(actions) == 0: # Cannot advance
            # cannot advance, backtrack
            self.dead |= {(self.tile_x, self.tile_y)}

            # Get rid of the blocking move
            self.moves = self.moves[:-1]

            # Go back to the last valid tile
            actions.append(self.moves[-1])

            # print("comment Action %s" % str(actions))

        return actions

    def successors(self):
        # print("comment Known Walls %s" % str(self.walls))
        # print("comment Successors: %s" % self.actions())
        return frozenset(self.actions())

    def eval(self, new_tile):
        x = new_tile[0]
        y = new_tile[1]

        euclid = math.sqrt((abs(self.goalTile - x)**2) + (abs(self.goalTile - y)**2))
        # manhat = abs(self.goalTile - x) + abs(self.goalTile - y)

        # h_cost = (manhat+euclid)/2
        # print(f"comment tile ({x}, {y}), h-cost {h_cost}", flush=True)

        return self.pathcost + euclid

    def deterministicPath(self,numPaths):
    ############ take pre-determined best route ###########
        actions = []
                        # sufficient exploration?

        # init min cost, location in list of paths, and path itself
        self.minPathIndx = 0
        minCost = float('inf')
        minIndex = 0
        minPath = []
        print(f"comment deterministic paths choices: {self.paths}")
        for i in range(numPaths):
            if self.paths[i][1] < minCost and len(self.paths[i][0]) > 10:
                minCost = self.paths[i][1] # !!
                minIndex = i
                minPath = self.paths[i][0]
                print(f"comment minPath in dPath: {minPath}")
        
        # need path in correct orientation (either 0,0 to 10,10 or vice versa)
        if self.goalTile == self.paths[minIndex][2]:
            print(f"comment front-facing")
            actions = minPath
            if actions[-1] != (self.goalTile, self.goalTile):
              print("comment appending goal tile")
              actions.append((self.goalTile, self.goalTile))
            print(f"comment actions: {actions}")
            if actions[0] == (self.tile_x, self.tile_y):
                print(f"comment removing first tile")
                actions = actions[1:] # already at first tile
            print(f"comment actions: {actions}")
            return actions
        else:
            print(f"comment reverse-facing")
            actions = minPath[::-1]
            if actions[-1] != (self.goalTile, self.goalTile):
              print("comment appending goal tile")
              actions.append((self.goalTile, self.goalTile))
            if actions[0] == (self.tile_x, self.tile_y):
                print(f"comment removing first tile")
                actions = actions[1:] # already at first tile
            print(f"comment actions: {actions}")
            return actions
            
    #######################################################

# Setup bot
bot = Bot(11)

# Setup A*
frontier = queue.PriorityQueue()
for successor in bot.successors():
    print(f"comment successor: {successor}")
    frontier.put((bot.eval(successor), successor))
    # print(f"comment added succ")

# frontier.put((bot.pathcost, bot.current_tile()))
if frontier.qsize() > 1: 
    if random.random() > 0.5:
        dq = frontier.get()
        print(f"comment dq: {dq}")
        frontier.put(dq)

    

# Wait a few seconds for some initial sense data
print("himynameis A-Star-Bot", flush=True)
time.sleep(0.25)

# minPath = []
# pathIdx = 0
# searching = True

while True:
    # print(f"comment true")
    # while there is new input on stdin:
    while select.select([sys.stdin,],[],[],0.0)[0]:
        # read and process the next 1-line observation
        obs = sys.stdin.readline()
        # print(f"comment obs {obs}")
        obs = obs.split(" ")
        # print(f"comment obs {obs}")
        # print("comment obs: %s" % obs, flush=True)
        if obs == []:
            pass
    
        elif obs[0] == "bot":
            # update our own position
            x = float(obs[1])
            y = float(obs[2])
            # print("comment now at: %s %s" % (x,y), flush=True)
            # print('comment Queue: %s' % frontier.queue, flush=True)
            # update our latest tile reached once we are firmly on the inside of the tile
            if ((int(x) != bot.tile_x or int(y) != bot.tile_y) and
                ((x-(int(x)+0.5))**2 + (y-(int(y)+0.5))**2)**0.5 < 0.2):
                # bot.tile_x = int(x)
                # bot.tile_y = int(y)
                current_tile = (int(x), int(y))
                bot.step(current_tile)
                  
                print(f"comment stepped to tile {int(x), int(y)}, pathcost: {bot.pathcost}")
                
                # print("comment moves: %s" % bot.moves, flush=True)
                # print("comment walls: %s" % bot.walls, flush=True)
                # print("comment seen: %s" % bot.seen, flush=True)
                # print("comment dead: %s" % bot.dead, flush=True)
                if bot.goal():
                    if bot.goalTile == 10: print("comment Reached the flag! Congrats!", flush=True)
                    bot.cacheMoves()
                    bot.changeGoal()
                    print("comment New goal: %s" % bot.goalTile, flush=True)

                    numPaths = len(bot.paths)
                    if numPaths >= 3:
                        newMoves = bot.deterministicPath(numPaths)
                        frontier.queue.clear()
                        print(f"comment adding minPath: {newMoves}")
                        bot.searching = False
                        bot.minPath = newMoves

        ########### don't need frontier, can just feed moves in via list #############
                        # for move in newMoves:
                        #     print(f"comment new move: {move}")
                        #     frontier.put((bot.eval(move),move))

                #   bot.cacheMoves()


                if bot.searching:
                  for successor in bot.successors():
                      frontier.put((bot.eval(successor), successor))
                else:
                    successor = bot.minPath[bot.minPathIndx]
                    print(f"comment current position: {bot.tile_x}, {bot.tile_y}")
                    print(f"comment getting next tile: {successor} from minPath: {bot.minPath}")
                    bot.minPathIndx += 1
                    frontier.put((bot.eval(successor), successor))
                
                # print("comment goal tile %s" % bot.goalTile, flush=True)
                # print("comment moves: %s" % bot.moves, flush=True)
                # print("comment seen tiles %s" % bot.seen, flush=True)
                # print("comment dead tiles %s" % bot.dead, flush=True)        
                # print("comment now at tile: %s %s" % (bot.tile_x, bot.tile_y), flush=True)
            
        elif obs[0] == "wall":
            # print("comment wall: %s %s %s %s" % (obs[1],obs[2],obs[3],obs[4]), flush=True)
            # ensure every wall we see is tracked in our walls set
            x0 = int(float(obs[1]))
            y0 = int(float(obs[2]))
            x1 = int(float(obs[3]))
            y1 = int(float(obs[4]))
            bot.walls |= {(x0,y0,x1,y1)}
        
        if obs == "close": 
            exit(0)
    
        if not frontier.empty():
            # print("comment %s" % str(frontier.queue))
            item = frontier.get()
            # print("comment %s" % str(item))
            next_tile = item[1]
            print(f"comment current position: {bot.tile_x}, {bot.tile_y}")
            print(f"comment next_tile frontier: {item[1]}")


            # print(f"comment next tile = {next_tile[0]} , {next_tile[1]}")
            # We've now seen the tile we're on
            bot.seen |= {(bot.tile_x, bot.tile_y)}
            x = next_tile[0] + 0.5
            y = next_tile[1] + 0.5

            frontier.queue.clear()

            if len(bot.moves) == 0 or bot.moves[-1] != (next_tile[0], next_tile[1]):
                #   print("comment here")
                bot.moves.append((next_tile[0], next_tile[1]))
            
            # print('comment Move List: %s' % bot.moves, flush=True)

            print("toward %s %s" % (x,y), flush=True)
            # print("comment ", flush=True)

            
    print("", flush=True)
    time.sleep(0.125)
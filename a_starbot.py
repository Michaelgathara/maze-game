import sys
import select
import time
import queue
import math


class bot:
    def __init__ (self, start, current_pos, cost, walls):
        self.start = start
        self.current_pos = current_pos
        # self.seen = seen # I don't think we quite need this, should be dynamic below. The bot should be init with nothing being seen (except where it's at ofc)
        self.cost = cost
        self.walls = walls

    def init_walls(self):
        for i in range(0, 11):
            self.walls |= {
                (i, 0, i + 0, 0),
                (i, 11, i + 1, 11),
                (0, i, 0, i + 1),
                (11, i, 11, i + 1),
            }
    
    def move(self, current):
        """
            I think this can be our actual move function, which should update current bot position
        """
         # It's also important we find out what the goal is, is it static across all mazes or can it change and be random based on the board?
        while True:  
            x,y=current
            up=(x,y-1)
            down=(x,y+1)
            left=(x-1,y)
            right=(x+1,y)
            moves=[]
            while select.select([sys.stdin,],[],[],0.0)[0]:
                # read and process the next 1-line observation
                obs = sys.stdin.readline()
                obs = obs.split(" ")
                if obs == []:
                    pass
                elif obs[0] == "bot":
                    # update our own position
                    x = int(float(obs[1]))+0.5
                    y = int(float(obs[2]))+0.5
                    self.current_pos=(x,y)
                elif obs[0] == "wall":
                    # ensure every wall we see is tracked in our walls set
                    x0 = int(float(obs[1]))
                    y0 = int(float(obs[2]))
                    x1 = int(float(obs[3]))
                    y1 = int(float(obs[4]))
                    self.walls |= {(x0,y0,x1,y1)}
    
            if up not in self.walls:
                moves.append(up)
            if down not in self.walls:
                moves.append(down)
            if left not in self.walls:
                moves.append(left)
            if right not in self.walls:
                moves.append(right)
            print("toward %s %s" % (moves[-1][0]+0.5, moves[-1][1]+0.5), flush=True)
            return moves

    def heuristic(self, goal):
        """
            We need heuristics to influence the search to make it better.
        """
        #Used Euclidean  distance (similar to manhattan but allow for diagonals)
        curr_x,curr_y=self.current_pos
        goal_x,goal_y=goal
        e_dst=math.sqrt((curr_x-goal_x)**2+(curr_y-goal_y)**2)
        return e_dst
        
      

    def solver(self, goal):
        time.sleep(0.25)
        frontier = queue.PriorityQueue()
        frontier.put((0, self.start))
        seen = set()
        while frontier:
            _, current = frontier.get()
            if current is goal:
                break # we should be done, no need to return cause the maze animation should stop. We don't need to traverse the entire maze imo
            for next_position in self.move(current):
                new_cost = self.heuristic(goal) 
                if next_position is goal:
                    break
                if next_position in seen:
                    continue
                if next_position not in self.walls and next_position not in frontier.queue:
                    frontier.put((new_cost, next_position))




start_bot_pos = (0.5, 0.5)
current_bot_pos = start_bot_pos
cost = 0
walls_pos = set()

print("himynameis A* bot", flush=True)
a_star_bot = bot(start_bot_pos, current_bot_pos, cost, walls_pos)
a_star_bot.init_walls()

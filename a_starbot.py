import math
import sys
import select
import time
from queue import PriorityQueue
import logging
import logging.handlers
from queue import Queue
import threading

log_queue = Queue(-1) 
queue_handler = logging.handlers.QueueHandler(log_queue)
logger = logging.getLogger('maze-logs')
logger.setLevel(logging.DEBUG)
logger.addHandler(queue_handler)

def log_writer(queue, log_filename):
    file_handler = logging.FileHandler(log_filename)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    while True:
        record = queue.get()
        if record is None: 
            break
        file_handler.handle(record)

log_thread = threading.Thread(target=log_writer, args=(log_queue, 'logs/output.log'))
log_thread.start()

class Bot:

    def __init__(self):
        self.cost = 0
        self.x = 0.5
        self.y = 8.5
        self.ty = -1
        self.tx = -1
        self.goal_x = 10
        self.goal_y = 10
        self.seen = set()
        self.dead = set()
        self.path = []
        self.planned_path = []
        self.backtrack_stack = []
        self.walls = set()
        self.is_at_start = True

        for i in range(0, 11):
            self.walls |= {(i, 0, i + 1, 0), (i, 11, i + 1, 11), (0, i, 0, i + 1), (11, i, 11, i + 1)}
        print("himynameis A* bot", flush=True)
        time.sleep(0.25)

    def actions(self):
        possible_actions = []
        # """
        # two tiles movement?"""
        # if len(self.seen) > 0 and (self.tx, self.ty + 2) not in (self.dead | self.seen) and (self.tx, self.ty, self.tx, self.ty + 2) not in self.walls:
        #     possible_actions.append((self.tx, self.ty + 2))  # move down
        # if len(self.seen) > 0 and (self.tx + 2, self.ty) not in (self.dead | self.seen) and (self.tx + 1, self.ty, self.tx + 2, self.ty) not in self.walls:
        #     possible_actions.append((self.tx + 2, self.ty))  # move right
        # if len(self.seen) > 0 and (self.tx, self.ty - 2) not in (self.dead | self.seen) and (self.tx, self.ty, self.tx, self.ty - 2) not in self.walls:
        #     possible_actions.append((self.tx, self.ty - 2))  # move up
        # if len(self.seen) > 0 and (self.tx - 2, self.ty) not in (self.dead | self.seen) and (self.tx, self.ty, self.tx - 2, self.ty) not in self.walls:
        #     possible_actions.append((self.tx, self.ty - 2))  # move left

        if len(self.seen) > 0 and (self.tx, self.ty + 1) not in (self.dead | self.seen) and (self.tx, self.ty + 1, self.tx + 1, self.ty + 1) not in self.walls:
            possible_actions.append((self.tx, self.ty + 1))  # move down
        if len(self.seen) > 0 and (self.tx + 1, self.ty) not in (self.dead | self.seen) and (self.tx + 1, self.ty, self.tx + 1, self.ty + 1) not in self.walls:
            possible_actions.append((self.tx + 1, self.ty))  # move right


        if len(self.seen) > 0 and (self.tx, self.ty - 1) not in (self.dead | self.seen) and (self.tx, self.ty, self.tx + 1, self.ty) not in self.walls:
            possible_actions.append((self.tx, self.ty - 1))  # move up
        if len(self.seen) > 0 and (self.tx - 1, self.ty) not in (self.dead | self.seen) and (self.tx, self.ty, self.tx, self.ty + 1) not in self.walls:
            possible_actions.append((self.tx - 1, self.ty))  # move left


        """
        diagonal movement?"""
        # if (self.tx - 1, self.ty - 1) not in (self.dead | self.seen) and (self.tx, self.ty, self.tx + 1, self.ty + 1) not in self.walls:
        #     possible_actions.append((self.tx + 1, self.ty + 1))  # move left

        # directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # down, right, up, left
        # for dx, dy in directions:
        #     x1, y1 = self.tx + dx, self.ty + dy
        #     x2, y2 = self.tx + 2 * dx, self.ty + 2 * dy
        #     if (x1, y1) not in (self.dead | self.seen) and (x1, y1, x1 + dx, y1 + dy) not in self.walls:
        #         if (x2, y2) not in (self.dead | self.seen) and (x2, y2, x2 + dx, y2 + dy) not in self.walls:
        #             possible_actions.append((x2, y2))  # move two tiles
        #         else:
        #             possible_actions.append((x1, y1))  # move one tile

        # Handle backtracking
        if len(possible_actions) == 0:
            if self.backtrack_stack:
                backtrack_to = self.backtrack_stack.pop()
                possible_actions.append(backtrack_to)
            else:
                self.dead.add((self.tx, self.ty))
        else:
            self.backtrack_stack.append((self.tx, self.ty))

        logger.warning(f"The possible actions: {possible_actions}")
        return possible_actions

    def astar(self):
        if self.is_at_start and self.tx == self.home_x and self.ty == self.home_y:
            
            self.is_at_start = False
            self.goal_x = 10
            self.goal_y = 10

        elif not self.is_at_start and self.tx == self.goal_x and self.ty == self.goal_y:
            

            self.is_at_start = True
            self.goal_x = self.home_x
            self.goal_y = self.home_y

        start = (self.tx, self.ty)
        goal = (self.goal_x, self.goal_y)
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {}
        cost_so_far = {start: 0}

        while not frontier.empty():
            _, current = frontier.get()

            for next_node in self.actions():
                # check the type of possible actions and if it is right then give it a cost of 1, down a cost of 2, left a cost of 3 and up a cost of 4
                cost = 1
                if next_node[1] < current[1]:
                    cost = 4  # up
                # elif next_node[0] > current[0]:
                #     cost = 3  # left
                # elif next_node[1] > current[1]:
                #     cost = 1  # down
                # else:
                #     cost = 2  # right

                new_cost = cost_so_far[current] + cost
                try:
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        frontier.empty()
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + self.heuristic(goal, next_node)
                        logger.error(f"The priority queue: {(priority, next_node)}")
                        frontier.put((priority, next_node))
                        came_from[next_node] = current
                except:
                    print(f"comment {cost_so_far}")
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        self.planned_path = path
        return path

    def heuristic(self, goal, current): #Euc distance
        return math.sqrt(((goal[0] - current[0]) ** 2) + ((goal[1] - current[1]) ** 2))
    
    def m_heuritic(self, goal, current):
        return abs(goal[0] - current[0]) + abs(goal[1] - current[1])
    
    def c_heuristic(self, goal, current):
        """
        TRASH"""
        first = abs(goal[0] - current[0])
        second = abs(goal[1] - current[1])
        return max(first, second)

if __name__ == "__main__":
    bot = Bot()
    # bot.main()
    last_toward = None
    while True:
        while select.select([sys.stdin, ], [], [], 0.0)[0]:
            obs = sys.stdin.readline()
            obs = obs.split(" ")
            if obs == []:
                pass
            elif obs[0] == "bot":
                x = float(obs[1])
                y = float(obs[2])
                if (int(x) != bot.tx or int(y) != bot.ty) \
                    and (
                        (x - (int(x) + 0.5)) ** 2 
                        + (y - (int(y) + 0.5)) ** 2) \
                        ** 0.5 < 0.2:
                    bot.tx = int(x)
                    bot.ty = int(y)

                    # bot.seen.add((bot.tx, bot.ty))
                    if not bot.path:
                        bot.path = [(bot.tx, bot.ty)]
                        bot.home_x = bot.tx
                        bot.home_y = bot.ty
                        bot.seen = set(bot.path)

            elif obs[0] == "wall":
                x0 = int(float(obs[1]))
                y0 = int(float(obs[2]))
                x1 = int(float(obs[3]))
                y1 = int(float(obs[4]))
                # wall = {(x0, y0, x1, y1)}
                # if wall not in bot.walls:
                bot.walls |= {(x0, y0, x1, y1)}

        if bot.path:
            if len(bot.path) > 0 and bot.path[-1] == (bot.tx, bot.ty):
                bot.seen |= {(bot.tx, bot.ty)}
                if bot.path[-1] == (bot.home_x,  bot.home_y):
                    bot.dead -= {(10, 10)}
                    bot.seen = {(bot.tx, bot.ty)}
                if bot.path[-1] == (10, 10):
                    planset = set(bot.path)
                    bot.dead = set()
                    for i in range(11):
                        for j in range(11):
                            if (i, j) not in planset:
                                bot.dead |= {(i, j)}
                    bot.seen = set()

                bot.path = bot.astar()
            bot.dead.union({(5.5, 10.5)})   
            time.sleep(0.5)
            current_toward = (bot.path[-1][0] + 0.5, bot.path[-1][1] + 0.5)
            if current_toward != last_toward:
                print("toward %s %s" % current_toward, flush=True)
                last_toward = current_toward
        print("", flush=True)
        time.sleep(0.125)
    
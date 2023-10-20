import math
import sys
import select
import time
from queue import PriorityQueue

terminal = sys.stdout
logger = open("logs/output.log", "w")

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

    def successors(self):
        fs = frozenset()
        for i in self.actions():
            fs |= {i}
        return fs

    def actions(self):
        possible_actions = []

        if len(self.seen) > 0 and (self.tx, self.ty + 1) not in (self.dead | self.seen) and (self.tx, self.ty + 1, self.tx + 1, self.ty + 1) not in self.walls:
            possible_actions.append((self.tx, self.ty + 1))  # move down
        if len(self.seen) > 0 and (self.tx + 1, self.ty) not in (self.dead | self.seen) and (self.tx + 1, self.ty, self.tx + 1, self.ty + 1) not in self.walls:
            possible_actions.append((self.tx + 1, self.ty))  # move right
        if len(self.seen) > 0 and (self.tx, self.ty - 1) not in (self.dead | self.seen) and (self.tx, self.ty, self.tx + 1, self.ty) not in self.walls:
            possible_actions.append((self.tx, self.ty - 1))  # move up
        if len(self.seen) > 0 and (self.tx - 1, self.ty) not in (self.dead | self.seen) and (self.tx, self.ty, self.tx, self.ty + 1) not in self.walls:
            possible_actions.append((self.tx - 1, self.ty))  # move left
        
        if len(possible_actions) == 0:
            if self.backtrack_stack:
                backtrack_to = self.backtrack_stack.pop()
                possible_actions.append(backtrack_to)
            else:
                self.dead |= {(self.tx, self.ty)}
        else:
            self.backtrack_stack.append((self.tx, self.ty))

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
            sys.stdout = logger
            print(f"F: {frontier}")
            sys.stdout = terminal

            for next_node in self.actions():
                dx = abs(current[0] - next_node[0])
                dy = abs(current[1] - next_node[1])
                cost = 1.414 if dx == 1 and dy == 1 else 1  # 1.414 is sqrt(2), the diagonal distance
                
                new_cost = cost_so_far[current] + cost
                try:
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + self.heuristic(goal, next_node)
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

    def heuristic(self, goal, current):
        return math.sqrt((goal[0] - current[0]) ** 2 + (goal[1] - current[1]) ** 2)
    

if __name__ == "__main__":
    bot = Bot()
    # bot.main()

    while True:
        while select.select([sys.stdin, ], [], [], 0.0)[0]:
            obs = sys.stdin.readline()
            obs = obs.split(" ")
            if obs == []:
                pass
            elif obs[0] == "bot":
                x = float(obs[1])
                y = float(obs[2])
                if (int(x) != bot.tx or int(y) != bot.ty) and (
                        (x - (int(x) + 0.5)) ** 2 + (y - (int(y) + 0.5)) ** 2) ** 0.5 < 0.2:
                    bot.tx = int(x)
                    bot.ty = int(y)
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
                bot.walls |= {(x0, y0, x1, y1)}
                
        if bot.path:
            if len(bot.path) > 0 and bot.path[-1] == (bot.tx, bot.ty):
                bot.seen |= {(bot.tx, bot.ty)}
                if bot.path[-1] == (bot.home_x, bot.home_y):
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
            time.sleep(2)
            print("toward %s %s" % (bot.path[-1][0] + 0.5, bot.path[-1][1] + 0.5), flush=True)
        print("", flush=True)
        time.sleep(0.125)
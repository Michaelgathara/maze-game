import sys
import select
import time
import queue
import math

class Bot:
    def __init__(self, start, goal):
        self.start = start
        self.goal = goal
        self.current_pos = start
        self.walls = set(self.init_walls())
        self.came_from = {}
        
    def init_walls(self):
        walls = []
        for i in range(0, 11):
            walls.extend([(i, 0), (i, 11), (0, i), (11, i)])
        return walls

    def heuristic(self, pos):
        return math.sqrt((pos[0] - self.goal[0]) ** 2 + (pos[1] - self.goal[1]) ** 2)

    def move(self):
        frontier = queue.PriorityQueue()
        frontier.put((0, self.start))
        cost_so_far = {self.start: 0}

        while not frontier.empty():
            _, current = frontier.get()

            if current == self.goal:
                break

            x, y = current
            neighbors = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]

            for next_pos in neighbors:
                if next_pos in self.walls:
                    continue
                
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(next_pos)
                    frontier.put((priority, next_pos))
                    self.came_from[next_pos] = current

    def reconstruct_path(self):
        current = self.goal
        path = []
        while current != self.start:
            path.append(current)
            current = self.came_from[current]
        path.append(self.start)
        return path[::-1]

print("himynameis A* bot", flush=True)
bot = Bot((0.5, 0.5), (10.5, 10.5))
bot.move()
path = bot.reconstruct_path()

for step in path:
    print(f"toward {step[0] + 0.5} {step[1] + 0.5}", flush=True)

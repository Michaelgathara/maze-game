import sys
import select
import time
import queue


class bot:
    def init(self, start, current_pos, cost, walls):
        self.start = start
        self.current_pos = current_pos
        # self.seen = seen # I don't think we quite need this, should be dynamic below. The bot should be init with nothing being seen (except where it's at ofc)
        self.cost = cost
        self.walls = walls

    def walls(self):
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
        pass

    def heuristic(self, goal):
        """
            We need heuristics to influence the search to make it better.
        """

        # It's also important we find out what the goal is, is it static across all mazes or can it change and be random based on the board?
        pass

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

        # while True:
        #     while select.select([sys.stdin,],[],[],0.0)[0]:
        #         obs = sys.stdin.readline()
        #         obs = obs.split(" ")
        #         if obs == []: pass
        #         elif obs[0] == "bot":
        #         self.current_pos=(float(obs[1]),float(obs[2]))
        #         pass


start_bot_pos = (0.5, 0.5)
current_bot_pos = start_bot_pos
cost = 0
walls_pos = set()

print("himynameis A* bot", flush=True)
a_star_bot = bot(start_bot_pos, current_bot_pos, cost, walls_pos)
# Should I call walls ?
# a_star_bot.walls()

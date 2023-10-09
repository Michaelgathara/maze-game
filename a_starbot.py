import sys
import select
import time
import queue
import math

terminal = sys.stdout
log = open("moves.log", "w")
obsLog = open("obs.log", "w")


class bot:
    def __init__(self, start, current_pos, cost, walls, seen):
        self.start = start
        self.current_pos = current_pos
        self.seen = seen # I don't think we quite need this, should be dynamic below. The bot should be init with nothing being seen (except where it's at ofc)
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
        while True:
            x, y = current
            moves = []

            while select.select(
                [
                    sys.stdin,
                ],
                [],
                [],
                0.0,
            )[0]:
                obs = sys.stdin.readline().split()

                if obs == []:
                    continue

                if obs[0] == "bot":
                    x = float(obs[1])
                    y = float(obs[2])
                    self.current_pos = (x, y)

                elif obs[0] == "wall":
                    x0 = int(float(obs[1]))
                    y0 = int(float(obs[2]))
                    x1 = int(float(obs[3]))
                    y1 = int(float(obs[4]))
                    self.walls |= {(x0, y0, x1, y1)}

                sys.stdout = obsLog
                print(f"Obs is {obs}\n")
                sys.stdout = terminal

            next_positions = [(x, y - 1), 
                              (x, y + 1), 
                              (x - 1, y), 
                              (x + 1, y)]

            for pos in next_positions:
                if (x, y, pos[0], pos[1]) not in self.walls and (x, y, pos[0], pos[1]) not in self.seen:
                    moves.append(pos)
                    self.seen.add((x, y, pos[0], pos[1]))

            sys.stdout = log
            print(f"The moves are {moves}\n")
            sys.stdout = terminal

            best_move = min(moves, key=lambda move: self.heuristic(move), default=None)

            if best_move: 
                move_x, move_y = best_move
            else:
                move_x, move_y = moves[-1]

            print("toward %s %s" % ((move_x * -1) + 0.5, move_y + 0.5), flush=True)
            return moves
            # if best_move:
                
            # else:
            #     print("toward %s %s" % (move_x + 0.5, move_y + 0.5), flush=True)

    # def move(self, current):
    #     """
    #     I think this can be our actual move function, which should update current bot position
    #     """
    #     # It's also important we find out what the goal is, is it static across all mazes or can it change and be random based on the board?
    #     while True:
    #         x, y = current
    #         up = (x, y - 1)
    #         down = (x, y + 1)
    #         left = (x - 1, y)
    #         right = (x + 1, y)
    #         moves = []
    #         while select.select(
    #             [
    #                 sys.stdin,
    #             ],
    #             [],
    #             [],
    #             0.0,
    #         )[0]:
    #             # read and process the next 1-line observation
    #             obs = sys.stdin.readline()
    #             obs = obs.split(" ")
    #             if obs == []:
    #                 pass
    #             elif obs[0] == "bot":
    #                 # update our own position
    #                 x = int(float(obs[1])) + 0.5
    #                 y = int(float(obs[2])) + 0.5
    #                 self.current_pos = (x, y)
    #             elif obs[0] == "wall":
    #                 # ensure every wall we see is tracked in our walls set
    #                 x0 = int(float(obs[1]))
    #                 y0 = int(float(obs[2]))
    #                 x1 = int(float(obs[3]))
    #                 y1 = int(float(obs[4]))
    #                 self.walls |= {(x0, y0, x1, y1)}

    #         if up not in self.walls:
    #             moves.append(up)
    #         if down not in self.walls:
    #             moves.append(down)
    #         if left not in self.walls:
    #             moves.append(left)
    #         if right not in self.walls:
    #             moves.append(right)
    #         print("toward %s %s" % (moves[-1][0] + 0.5, moves[-1][1] + 0.5), flush=True)
    #         return moves

    def heuristic(self, goal):
        """
        We need heuristics to influence the search to make it better.
        """
        # Used Euclidean  distance (similar to manhattan but allow for diagonals)
        curr_x, curr_y = self.current_pos
        goal_x, goal_y = goal
        e_dst = math.sqrt((curr_x - goal_x) ** 2 + (curr_y - goal_y) ** 2)
        return e_dst

    def solver(self, goal):
        time.sleep(0.25)
        frontier = queue.PriorityQueue()
        frontier.put((0, self.start))
        while frontier:
            _, current = frontier.get()
            if current is goal:
                break  # we should be done, no need to return cause the maze animation should stop. We don't need to traverse the entire maze imo
            for next_position in self.move(current):
                new_cost = self.heuristic(goal)
                if next_position is goal:
                    break
                if next_position in self.seen:
                    continue
                if (
                    next_position not in self.walls
                    and next_position not in frontier.queue
                ):
                    frontier.put((new_cost, next_position))


start_bot_pos = (0.5, 0.5)
current_bot_pos = start_bot_pos
cost = 0
walls_pos = set()
seen = set(start_bot_pos)

print("himynameis A* bot", flush=True)
a_star_bot = bot(start_bot_pos, current_bot_pos, cost, walls_pos, seen)
a_star_bot.init_walls()
# I just did 10.5,10.5 to test this will need to be the flag
a_star_bot.solver((10.5, 10.5))
log.close()
obsLog.close()

# import sys
# import select
# import time
# import heapq
# import math

# # Define constants for the maze dimensions
# MAZE_SIZE = 11

# # Define constants for the possible directions
# DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# # Define the initial position
# x = 0
# y = 0

# # Define the goal position
# goal_x = MAZE_SIZE
# goal_y = MAZE_SIZE

# # Create a set of walls known
# walls = set()

# # Heuristic function (Euclidean distance)
# def heuristic(pos):
#     return math.sqrt((pos[0] - goal_x) ** 2 + (pos[1] - goal_y) ** 2)

# # A* algorithm
# open_list = [(0, (0, 0))]
# came_from = {}
# g_scores = {(0, 0): 0}
# f_scores = {(0, 0): heuristic((0, 0))}

# # introduce ourselves, all friendly like
# print("himynameis AStar-bot", flush=True)

# # Wait a few seconds for some initial sense data
# time.sleep(0.25)

# while True:
#     # while there is new input on stdin:
#     while select.select([sys.stdin, ], [], [], 0.0)[0]:
#         # read and process the next 1-line observation
#         obs = sys.stdin.readline()
#         obs = obs.split(" ")
#         if obs == []:
#             pass
#         elif obs[0] == "bot":
#             # update our own position
#             x = int(float(obs[1]))
#             y = int(float(obs[2]))
#         elif obs[0] == "wall":
#             x0 = int(float(obs[1]))
#             y0 = int(float(obs[2]))
#             x1 = int(float(obs[3]))
#             y1 = int(float(obs[4]))
#             walls.add((x0, y0, x1, y1))

#     if (x, y) == (goal_x, goal_y):
#         # If we have reached the goal, we can backtrack to find the path
#         path = reconstruct_path(came_from, (x, y))
#         path.reverse()
#         print("Path:", path, flush=True)
#     else:
#         # Use A* algorithm to update the path
#         current = (x, y)
#         for dx, dy in DIRECTIONS:
#             neighbor = (x + dx, y + dy)
#             if neighbor in walls:
#                 continue
#             tentative_g_score = g_scores[current] + 1
#             if neighbor not in g_scores or tentative_g_score < g_scores[neighbor]:
#                 came_from[neighbor] = current
#                 g_scores[neighbor] = tentative_g_score
#                 f_scores[neighbor] = g_scores[neighbor] + heuristic(neighbor)
#                 if (f_scores[neighbor], neighbor) not in open_list:
#                     heapq.heappush(open_list, (f_scores[neighbor], neighbor))

#         # Calculate the next move
#         if open_list:
#             current = min(open_list)[1]
#             next_x, next_y = current
#             x, y = next_x, next_y
#             print("toward %s %s" % (x + 0.5, y + 0.5), flush=True)
#         else:
#             print("No valid path found.", flush=True)

#     time.sleep(0.125)



import sys
import select
import time
import heapq
import math

# Define constants for the maze dimensions
MAZE_SIZE = 11

# Define constants for the possible directions
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# Define the initial position
x = 0.5
y = 0.5

# Define the goal position
goal_x = MAZE_SIZE - 0.5
goal_y = MAZE_SIZE - 0.5

# Create a set of walls known
walls = set()

# Heuristic function (Manhattan distance)
def heuristic(pos):
    return abs(pos[0] - goal_x) + abs(pos[1] - goal_y)

# A* algorithm
open_list = [(0, (0.5, 0.5))]
came_from = {}
g_scores = {(0.5, 0.5): 0}
f_scores = {(0.5, 0.5): heuristic((0.5, 0.5))}

# introduce ourselves, all friendly-like
print("himynameis AStar-bot", flush=True)

# Wait a few seconds for some initial sense data
time.sleep(1)

while True:
    # while there is new input on stdin:
    while select.select([sys.stdin, ], [], [], 0.0)[0]:
        # read and process the next 1-line observation
        obs = sys.stdin.readline()
        obs = obs.split(" ")
        if obs == []:
            pass
        elif obs[0] == "bot":
            # update our own position
            x = float(obs[1])
            y = float(obs[2])
        elif obs[0] == "wall":
            x0 = int(float(obs[1]))
            y0 = int(float(obs[2]))
            x1 = int(float(obs[3]))
            y1 = int(float(obs[4]))
            walls.add((x0, y0, x1, y1))

    if (x, y) == (goal_x, goal_y):
        # If we have reached the goal, we can backtrack to find the path
        path = reconstruct_path(came_from, (x, y))
        path.reverse()
        print("Path:", path, flush=True)
    else:
        # Use A* algorithm to update the path
        current = (x, y)
        valid_neighbors = []

        for dx, dy in DIRECTIONS:
            neighbor = (x + dx, y + dy)
            if neighbor in walls:
                continue
            tentative_g_score = g_scores[current] + 1
            if neighbor not in g_scores or tentative_g_score < g_scores[neighbor]:
                came_from[neighbor] = current
                g_scores[neighbor] = tentative_g_score
                f_scores[neighbor] = g_scores[neighbor] + heuristic(neighbor)
                valid_neighbors.append(neighbor)

        if not valid_neighbors:
            # No valid neighbors, backtrack
            if current == (0.5, 0.5):
                # We are back at the start, nowhere to go
                print("Nowhere to go. Stopping.", flush=True)
                break
            else:
                # Backtrack to the previous position
                previous = came_from[current]
                x, y = previous
                print("toward %s %s" % (x, y), flush=True)
                time.sleep(5)
        else:
            # Calculate the next move to a valid neighbor
            next_x, next_y = min(valid_neighbors, key=lambda pos: f_scores[pos])
            x, y = next_x, next_y
            print("toward %s %s" % (x, y), flush=True)
            time.sleep(5)

    time.sleep(1)

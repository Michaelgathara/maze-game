import sys
import select
import time
import heapq

MAZE_SIZE = 11
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

x, y = 0.5, 0.5
goal_x, goal_y = MAZE_SIZE - 0.5, MAZE_SIZE - 0.5
walls = set()

def heuristic(pos):
    return abs(pos[0] - goal_x) + abs(pos[1] - goal_y)

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from.keys():
        current = came_from[current]
        total_path.append(current)
    return total_path

print("himynameis AStar-bot", flush=True)
time.sleep(1)

final_path = []
path_found = False
while True:
    if not path_found:
        open_list = [(0, (x, y))]
        came_from = {}
        g_scores = {(x, y): 0}
        f_scores = {(x, y): heuristic((x, y))}

        while open_list:
            current = heapq.heappop(open_list)[1]

            if current == (goal_x, goal_y):
                final_path = reconstruct_path(came_from, current)
                path_found = True
                break

            for dx, dy in DIRECTIONS:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if neighbor in walls:
                    continue

                tentative_g_score = g_scores[current] + 1

                if neighbor not in g_scores or tentative_g_score < g_scores[neighbor]:
                    came_from[neighbor] = current
                    g_scores[neighbor] = tentative_g_score
                    f_scores[neighbor] = tentative_g_score + heuristic(neighbor)
                    heapq.heappush(open_list, (f_scores[neighbor], neighbor))

    if path_found:
        print("Path:", final_path, flush=True)
        for next_move in reversed(final_path[1:]):
            print("toward %s %s" % (next_move[0], next_move[1]), flush=True)
            time.sleep(1)
        break

    while select.select([sys.stdin, ], [], [], 0.0)[0]:
        obs = sys.stdin.readline()
        obs = obs.split(" ")
        if obs == []:
            pass
        elif obs[0] == "bot":
            x, y = float(obs[1]), float(obs[2])
        elif obs[0] == "wall":
            walls.add((int(float(obs[1])), int(float(obs[2])), int(float(obs[3])), int(float(obs[4]))))

    time.sleep(1)

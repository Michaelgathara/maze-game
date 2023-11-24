
import sys
import select
import time
import random
# from queue import PriorityQueue
from queue import Queue
import heapq
import logging
import logging.handlers
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

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = float('inf') # cost from start
        self.rhs = float('inf') # cost to reach goal whilst passing said node
        self.key = (float('inf'), float('inf')) # for da priority queue ordering and stuff

    def __lt__(self, other):
        return self.key < other.key

    def __repr__(self):
        return f"Node({self.x}, {self.y})"

    def g_value(self, node):
        return node.g

    def cost(self, node0, node1):
        if node1.rhs > node0.rhs:
            return node0.rhs
        return node1.rhs

class PriorityQueue:
    def __init__(self):
        self.elements = []
        self.entry_finder = {}
        self.REMOVED = '<removed>' 

    def is_empty(self):
        return not self.elements

    def put(self, node, priority):
        if node in self.entry_finder:
            self.remove(node)
        entry = [priority, node]
        self.entry_finder[node] = entry
        heapq.heappush(self.elements, entry)

    def get(self):
        while self.elements:
            priority, node = heapq.heappop(self.elements)
            if node is not self.REMOVED:
                del self.entry_finder[node]
                return node
        raise KeyError("pop from an empty priority queue")

    def remove(self, node):
        entry = self.entry_finder.pop(node)
        entry[-1] = self.REMOVED

    def update(self, node, priority):
        self.remove(node)
        self.put(node, priority)


class Graph:
    def __init__(self, width, height, nodes):
        self.width = width
        self.height = height
        self.nodes = nodes

    def get_neighbors(self, node):
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Adjacent cells (up, right, down, left)
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append(self.nodes[nx][ny])
        return neighbors

    def update_graph(self, updated_walls):
        # Handle the updates to the graph based on the new obstacle information
        pass


"""Some helpers and what not right here"""
def initialize_nodes(width, height):
    nodes = [[Node(x, y) for y in range(height)] for x in range(width)]
    return nodes

def calculate_key(node, goal_node, heuristic):
    return (min(node.g, node.rhs) + heuristic(node, goal_node), min(node.g, node.rhs))

def manhattan_distance(node_a, node_b):
    return abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)

def update_vertex(node):
    if node != goal_node:
        # Set node.rhs to the minimum rhs over all predecessors
        node.rhs = min([node.g_value(predecessor) + node.cost(predecessor, node) for predecessor in graph.get_neighbors(node)])
    if node in pq:
        pq.remove(node)
    if node.g != node.rhs:
        pq.put(node, calculate_key(node, start_node, goal_node, manhattan_distance))

width, height = 11, 11
nodes = initialize_nodes(width, height)
graph = Graph(width, height, nodes)

home_x = home_y = start_x = start_y = 0.5
goal_x, goal_y = 11, 11
start_node = nodes[start_x][start_y]
goal_node = nodes[goal_x][goal_y]

start_node.g = float('inf')
start_node.rhs = 0
goal_node.g = float('inf')
goal_node.rhs = 0

pq = PriorityQueue()
pq.put(goal_node, calculate_key(goal_node, start_node, goal_node, manhattan_distance))
 
while True:
    # Compute or update the shortest path
    while not pq.is_empty() and (pq.top().key < calculate_key(start_node, start_node, goal_node, manhattan_distance) or start_node.rhs != start_node.g):
        current_node = pq.get()
        if current_node.g > current_node.rhs:
            current_node.g = current_node.rhs
            for neighbor in graph.get_neighbors(current_node):
                update_vertex(neighbor)  # This function updates the neighbor's rhs and reinserts it in the priority queue if necessary
        else:
            current_node.g = float('inf')
            update_vertex(current_node)
            for neighbor in graph.get_neighbors(current_node):
                update_vertex(neighbor)
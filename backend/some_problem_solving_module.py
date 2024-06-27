# some_problem_solving_module.py - Version 1.0
# Emplacement: backend/some_problem_solving_module.py

import heapq

def solve_astar(problem_data):
    start, goal, graph = problem_data['start'], problem_data['goal'], problem_data['graph']
    open_set = [(0, start)]
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, goal)

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor, cost in graph[current].items():
            tentative_g_score = g_score[current] + cost
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None

def solve_dijkstra(problem_data):
    start, goal, graph = problem_data['start'], problem_data['goal'], problem_data['graph']
    queue = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    came_from = {}

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_node == goal:
            return reconstruct_path(came_from, current_node)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                came_from[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    return None

def heuristic(node, goal):
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

# Fin du fichier some_problem_solving_module.py - Version 1.0

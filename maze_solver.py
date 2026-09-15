"""Solve ASCII with the A* algorithme"""
import heapq

wall = "#"
path = "o"
explored = "*"

DIRECTIONS = [
    (-1, 0),
    (1, 0), 
    (0, -1),
    (0, 1),
]

def manhattan_distance(current, goal):
    current_row, current_column = current
    goal_row, goal_column = goal
    return abs(current_row - goal_row) + abs(current_column - goal_column)

def get_walkable_neighbors(grid, position):
    row, column = position
    neighgbors = []
    for row_change, column_change in DIRECTIONS:
        next_row = row + row_change
        next_column = column + column_change
        if 0 <= next_row < len(grid) and 0 <= next_column < len(grid[0]):
            if grid[next_row][next_column] != wall:
                neighgbors.append((next_row, next_column))
    return neighgbors

test_grid = [
    ["#", "#", "#"],
    ["#", ".", "."],
    ["#", "#", "#"],
]

print(get_walkable_neighbors(test_grid, (1, 1)))
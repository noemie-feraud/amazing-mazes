import json
import random
from intro import *

###     [INSTRUCTION 3: Maze should be a perfect one ; Use a recursive backtrack ]

# initialize starting point from maze
start_x, start_y = 1, 1
lab[start_y][start_x] = "."

# initialize neighbor to save each cell already visited
line_up = [(start_x, start_y)]

# create the function for DFS (Deep First Search)

while len(line_up) > 0:
    x, y = line_up[-1]
    # -1 to save border

    # Define the order movements right, down, left, up
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    random.shuffle(directions)
    # choose a random direction

    # Explore each direction
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + 2 * dx, y + 2 * dy
        # new position, where i want to go ( 2steps)

        if 0 < nx < matrix_size - 1 and 0 < ny < matrix_size - 1:
            # check if the position exist and available
            if lab[ny][nx] == "#":
                neighbors.append((nx, ny, dx, dy))
            # save as visited in neighbors

    if len(neighbors) > 0:
        # choose a neighbor and break wall
        nx, ny, dx, dy = neighbors[0]
        # if the next cell is a wall
        lab[y + dy][x + dx] = "."
        lab[ny][nx] = "."  # save new positions

        line_up.append((nx, ny))  # ad positions at the line up

    else:
        line_up.pop()  # backtracking changing position in line up search and choose a new cell

###     [ SAVE AS JSON FILES ]      ###

lab_json = [" ".join(line) for line in lab]
# display for json, transforms the list into a text string

with open(filename, "w", encoding="utf-8") as f:
    json.dump(lab_json, f, ensure_ascii=False, indent=1)

print(f"Maze created in your file {filename}")

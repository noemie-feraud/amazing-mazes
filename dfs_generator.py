import random
from collections import deque
from intro import *

###     [ INSTRUCTION 3: Perfect maze generation using Iterative Depth-First Search ]

# n represents the user input (number of corridors)
n = matrix_size
size = 2 * n + 1  # grid size is always (2n + 1)

wall, empty = "#", "."

# create the full grid
lab = [[wall for _ in range(size)] for _ in range(size)]

# Initialize starting point in the maze ( in the ASCII grid)
start_x, start_y = 1, 1
lab[start_y][start_x] = empty

# Initialize explicit stack (deque) for iterative LIFO backtracking
line_up = deque([(start_x, start_y)])

# Main DFS loop (Depth-First Search)
while len(line_up) > 0:
    x, y = line_up[-1]  # Peek at current top cell

    # Define random direction order: right, down, left, up
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    random.shuffle(directions)

    # Explore unvisited neighbors at a distance of 2 steps
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + 2 * dx, y + 2 * dy

        # Check if the cell is inside inner boundaries
        if 0 < nx < size - 1 and 0 < ny < size - 1:
            if lab[ny][nx] == wall:
                neighbors.append((nx, ny, dx, dy))

    if len(neighbors) > 0:
        # Pick the first random neighbor and carve the path
        nx, ny, dx, dy = neighbors[0]

        lab[y + dy][x + dx] = empty  # Break intermediate wall
        lab[ny][nx] = empty  # Open target cell

        line_up.append((nx, ny))  # Push new cell onto stack
    else:
        line_up.pop()  # Backtrack when hitting a dead end


###     [ INSTRUCTION 4: Open entrance at top-left and exit at bottom-right ]

# Opening coordinates matching the subject page 3 example
# Entrance at top-left corner
lab[0][0] = empty  # Corner (0,0)
lab[1][0] = empty  # Outer wall access

# Exit at bottom-right corner
lab[size - 1][size - 1] = empty  # Corner (2n, 2n)
lab[size - 2][size - 1] = empty  # Outer wall access


###     [ SAVE AS ASCII TEXT FILE ]


with open(filename, "w", encoding="utf-8") as f:
    for line in lab:
        f.write("".join(line) + "\n")

print(f"Maze created in your file {filename}")

# File to solve
input_file = input("Entrer le nom du fichier labyrinthe à résoudre : ")
if not input_file.endswith(".txt"):
    input_file += ".txt"

# saving solution in independant file
output_file = input("Entrer le nom du fichier pour le solveur: ")
if not output_file.endswith(".txt"):
    output_file += ".txt"

# Maze to ASCII
with open(input_file, "r", encoding="utf-8") as f:
    grid = [list(line.strip()) for line in f.readlines()]

# initialize grid
height = len(grid)
width = len(grid[0])

# initialize starting  and end point
start = (0, 0)
goal = (height - 1, width - 1)

# Down, Right, Up, Left
directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

# Stack stores lists: [y, x, k(path)]
# k = index of the next direction to test (0, 1, 2, 3)
stack = [[start[0], start[1], 0]]
visited = set([start])

found = False

# DFS solving loop
while stack:
    cadre = stack[-1]  # current pos
    curr_y, curr_x, k = cadre  # current pos in grid

    # if  Goal
    if (curr_y, curr_x) == goal:
        found = True
        break

    # 4 directions tested for this cell -> Backtrack
    if k == 4:
        stack.pop()  # impasse demi tour
        continue

    # Advance direction cursor
    cadre[2] = k + 1

    # current direction k
    dy, dx = directions[k]
    ny, nx = curr_y + dy, curr_x + dx

    # 5. Check validity next cell target
    if not (0 <= ny < height and 0 <= nx < width):  # if cell is in the grid
        continue
    if (ny, nx) in visited:  # if already visited
        continue
    if grid[ny][nx] == "#":  # if is  a wall
        continue

    # 6. mark visited and push to stack with k=0
    visited.add((ny, nx))  #  add in pile
    stack.append([ny, nx, 0])  # available move on


###     [ FINAL PATH WITH 'o' ]

if found:
    # La pile contient DIRECTEMENT le bon chemin
    # On la parcourt simplement pour marquer 'o'
    for cy, cx, _ in stack:
        grid[cy][cx] = "o"


###     [ SAVE SOLVED MAZE TO TEXT FILE ]

with open(output_file, "w", encoding="utf-8") as f:
    for line in grid:
        f.write("".join(line) + "\n")

print(f"Solution saved in {output_file}")

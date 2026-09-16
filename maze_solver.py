"""Solve ASCII with the A* algorithme"""
import heapq

wall = "#"
path = "o"
explored = "*"
#allows to move up, down, left and right
DIRECTIONS = [
    (-1, 0),
    (1, 0), 
    (0, -1),
    (0, 1),
]

def manhattan_distance(current, goal):
    #split positions such as (2, 5) into row and column
    current_row, current_column = current
    goal_row, goal_column = goal
    #estimate the distance without considering walls.
    return abs(current_row - goal_row) + abs(current_column - goal_column)

def get_walkable_neighbors(grid, position):
    #split the current position into row and column
    row, column = position
    neighgbors = [] #will contain the accessible neighboring position
    #try each allowed direction
    for row_change, column_change in DIRECTIONS:
        next_row = row + row_change
        next_column = column + column_change
        #check that the candidate position is inside the grid
        if 0 <= next_row < len(grid) and 0 <= next_column < len(grid[0]):
            #add it only when it is not a well
            if grid[next_row][next_column] != wall:
                neighgbors.append((next_row, next_column))
    return neighgbors

def solve_with_a_star(grid, start, goal):
    #reject a maze whose entrance or exit is a wall
    if grid[start[0]][start[1]] == wall or grid[goal[0]][goal[1]] == wall:
        raise ValueError("The entrance or exit is a wall")
    priority_queue = []
    #the start has a priority equal to its estimated remaining distance
    start_priority = manhattan_distance(start, goal)
    heapq.heappush(priority_queue, (start_priority, start))

    #stores the previous position for every discovered position
    came_from = {start: None}

    #stores the best known number of steps from start to each position
    cost_so_far = {start: 0}

    #stores positions that have already been fully processed
    explored_positions = set()

    #continue while there are positions left to explore
    while priority_queue:
        #get and remove the position with the smallest priority
        _, current = heapq.heappop(priority_queue)
        #ignore an old duplicate entry in the priority queue
        if current in explored_positions:
            continue
        #mark the current position as fully processed
        explored_positions.add(current)
        #stop searching when the goal is reached
        if current == goal:
            break
        #examine every accessible neighbor
        for neighbor in get_walkable_neighbors(grid, current):
            #moving to a neighbor costs one step
            new_cost = cost_so_far[current] + 1
            #keep this route only if it is new or shorter than the old one
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                #save the new best cost g
                cost_so_far[neighbor] = new_cost
                #calculate the priority f = g + h
                priority = new_cost + manhattan_distance(neighbor, goal)
                #remember how we reached this neighbor
                came_from[neighbor] = current
                #add the neighbor to the priority queue
                heapq.heappush(priority_queue, (priority, neighbor))

    #if the goal was never reached, raise an error
    if goal not in came_from:
        raise ValueError("No path found from start to goal.")
    #rebuild the path backwards: goal -> ... -> start
    path_positions = []
    current = goal
    while current is not None:
        path_positions.append(current)
        current = came_from[current]
    #put the path back in the normal order: start -> ... -> goal    
    path_positions.reverse()
    #copy th eoriginal maze so it remains unchanged
    solved_grid = [row.copy() for row in grid]
    #mark every explored position with *
    for row, column in explored_positions:
        solved_grid[row][column] = explored
    #overwrite the final path with o to make it more visible
    for row, column in path_positions:
        solved_grid[row][column] = path
    return solved_grid

def read_maze(file_name):
    # Read every non-empty line and turn each line into a list of characters.
    with open(file_name, "r", encoding="utf-8") as maze_file:
        grid = [list(line.rstrip("\n")) for line in maze_file if line.rstrip("\n")]

    if not grid:
        raise ValueError("The maze file is empty")

    # Check that every row has the same width.
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError("The maze must be rectangular")

    return grid


def write_maze(grid, file_name):
    # Write one ASCII row per line in the output file.
    with open(file_name, "w", encoding="utf-8") as maze_file:
        for row in grid:
            maze_file.write("".join(row) + "\n")


def main():
    input_file_name = input("Enter the maze input file name: ")
    output_file_name = input("Enter the solved maze output file name: ")

    # Add .txt when the user did not write the extension.
    if not input_file_name.endswith(".txt"):
        input_file_name += ".txt"

    if not output_file_name.endswith(".txt"):
        output_file_name += ".txt"

    grid = read_maze(input_file_name)

    # The project specification places the entrance and exit in opposite corners.
    start = (0, 0)
    goal = (len(grid) - 1, len(grid[0]) - 1)

    solved_grid = solve_with_a_star(grid, start, goal)
    write_maze(solved_grid, output_file_name)

    print(f"Solved maze saved in {output_file_name}")


if __name__ == "__main__":
    main()
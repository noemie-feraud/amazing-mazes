import heapq

# AJOUTÉ : module commun décrit au chapitre 01. Il possède la lecture du
# fichier, le marquage des 'o' et des '*', et l'écriture, pour que le solveur et le générateur ne dupliquent jamais ce code.
from grille import WALL, DIRECTIONS, read_maze, mark_solution, write_maze


###     [ INSTRUCTION 5: Maze solving using Iterative Depth-First Search ]

# MODIFIÉ : la résolution est maintenant dans une fonction, pour les mêmes
# raisons que dans generateur.py — appelable plusieurs fois, chronométrable, testable, et l'import ne pose plus de question à l'utilisateur.
#
# MODIFIÉ : on manipule des coordonnées de la grille LOGIQUE (i, j de 0 à n-1)
# au lieu des coordonnées d'affichage. On avance donc d'une case à la fois et non d'un caractère, et le mur entre deux cases se lit avec la formule du
# milieu du chapitre 01.

def backtracking(grid, size):
    """Relie l'entrée à la sortie et renvoie (path, visited)

    path   : liste ordonnée des cases de l'entrée vers la sortie
    visited : toutes les cases touchées, impasses comprises

    AJOUTÉ : la function renvoie ces deux valeurs au lieu d'écrire directement
    dans la grid. C'est la différence entre les deux qui donne les '*', et c'est ce dont mesures.py a besoin pour compter les cases explorées.
    """
    n = (size - 1) // 2
    goal = (n - 1, n - 1)

    # MODIFIÉ : un bytearray indexé remplace le set de tuples. Le test d'une
    # case devient un accès direct au lieu d'un calcul de hachage, et la mémoire tient dans un octet par case.
    visited = bytearray(n * n)
    visited[0] = 1

    # Stack stores lists: [i, j, k(path)]
    # k = index of the next direction to test (0, 1, 2, 3)
    # CONSERVÉ : ce curseur est l'idée principale du solveur. Sans lui, chaque
    # case serait réexaminée à chaque retour en arrière ; avec lui, les quatre directions d'une case sont testées une fois pour toutes.
    stack = [[0, 0, 0]]

    # DFS solving loop
    while stack:
        frame = stack[-1]  # current pos
        curr_i, curr_j, k = frame  # current pos in grid

        # if Goal
        # CONSERVÉ : on sort SANS dépiler. C'est ce qui fait que la pile contient encore le chemin complet à la fin.
        if (curr_i, curr_j) == goal:
            break

        # 4 directions tested for this cell -> Backtrack
        if k == 4:
            stack.pop()  # impasse demi tour
            continue

        # Advance direction cursor
        # CONSERVÉ : le curseur avance AVANT les tests. Qu'une direction mène quelque part ou qu'elle soit rejetée, elle ne sera jamais réexaminée.
        frame[2] = k + 1

        # current direction k
        di, dj = DIRECTIONS[k]
        ni, nj = curr_i + di, curr_j + dj

        # Check validity next cell target
        if not (0 <= ni < n and 0 <= nj < n):  # if cell is in the grid
            continue
        if visited[ni * n + nj]:  # if already visited
            continue
        # if is a wall
        # MODIFIÉ : formule du milieu du chapitre 01. Le caractère situé entre
        # les deux cases est en (i+ni+1, j+nj+1) ; s'il n'est pas un '#', le passage est ouvert. Ce test vient en dernier car c'est le plus coûteux.
        if grid[(curr_i + ni + 1) * size + (curr_j + nj + 1)] == WALL:
            continue

        # mark visited and push to stack with k=0
        visited[ni * n + nj] = 1  # add in pile
        stack.append([ni, nj, 0])  # available move on

    ###     [ FINAL PATH WITH 'o' ]

    # La pile contient DIRECTEMENT le bon chemin.
    # MODIFIÉ : au lieu de mark_solution la grille ici, on se contente d'extraire les
    # coordonnées en laissant tomber les curseurs de direction. Le marquage est fait par mark_solution(), dans grille.py, qui sert aussi à A*.
    path = [(frame[0], frame[1]) for frame in stack]
    return path, visited


###     [ INSTRUCTION 6: Maze solving with the A* algorithm ]

# Chapitre 04 de la documentation. Même signature que backtracking() :
# on renvoie (chemin, visitees), pour que les deux soient interchangeables

def manhattan_distance(current, goal):
    #split positions such as (2, 5) into row and column
    current_row, current_column = current
    goal_row, goal_column = goal
    #estimate the distance without considering walls.
    # CONSERVÉ : ignorer les murs ne peut que raccourcir le trajet, jamais
    # l'allonger. L'heuristique ne surestime donc jamais la distance restante, et c'est cette propriété qui garantit qu'A* trouve le plus court chemin.
    return abs(current_row - goal_row) + abs(current_column - goal_column)


def a_star(grid, size):
    """Recherche guidée par f = g + h. Renvoie (path, visited)"""
    n = (size - 1) // 2
    start = (0, 0)
    goal = (n - 1, n - 1)

    #reject a maze whose entrance or exit is a wall
    if grid[size + 1] == WALL or grid[(2 * n - 1) * size + (2 * n - 1)] == WALL:
        raise ValueError("The entrance or exit is a wall")

    # MODIFIÉ : trois listes indexées remplacent les dictionnaires à clés tuples.
    # Un accès direct au lieu d'un calcul de hachage, et beaucoup moins de
    # mémoire quand il y a un million de cases.
    #stores the best known number of steps from start to each position
    cost_so_far = [-1] * (n * n)
    cost_so_far[0] = 0
    #stores the previous position for every discovered position
    came_from = [-1] * (n * n)
    #stores positions that have already been fully processed
    explored_positions = bytearray(n * n)

    #the start has a priority equal to its estimated remaining distance
    # MODIFIÉ : on empile (f, g, case) et non (f, case). En cas d'égalité sur f, Python départage sur g, donc sans jamais comparer les coordonnées
    priority_queue = [(manhattan_distance(start, goal), 0, 0)]

    #continue while there are positions left to explore
    while priority_queue:
        #get and remove the position with the smallest priority
        _, g, current = heapq.heappop(priority_queue)

        #ignore an old duplicate entry in the priority queue
        # CONSERVÉ : une même case peut être empilée plusieurs fois, découverte
        # par plusieurs voisins. Un tas ne permet pas de modifier une entrée, on en ajoute donc une nouvelle et on ignore les périmées à la sortie
        if explored_positions[current]:
            continue
        #mark the current position as fully processed
        explored_positions[current] = 1
        #stop searching when the goal is reached
        # CONSERVÉ : on s'arrête quand l'arrivée SORT du tas, pas quand on la
        # découvre. Une case découverte est une candidate, son g peut encore être amélioré ; une case extraite est définitive
        if current == n * n - 1:
            break

        #examine every accessible neighbor
        # MODIFIÉ : la fonction get_walkable_neighbors() est déroulée ici, comme au chapitre 04. Elle construisait une liste par case examinée, soit un
        # million de listes inutiles à n = 1000. Mesuré : 13 % de temps en moins
        #split the current position into row and column
        row, column = divmod(current, n)
        #try each allowed direction
        for row_change, column_change in DIRECTIONS:
            next_row = row + row_change
            next_column = column + column_change
            #check that the candidate position is inside the grid
            if not (0 <= next_row < n and 0 <= next_column < n):
                continue
            #skip it when it is a wall
            # Le mur ne se lit pas sur la case voisine mais sur le caractère situé ENTRE les deux cases (formule du milieu, chapitre 01)
            if grid[(row + next_row + 1) * size + (column + next_column + 1)] == WALL:
                continue
            neighbor = (next_row, next_column)
            neighbor_index = next_row * n + next_column
            #moving to a neighbor costs one step
            new_cost = g + 1
            #keep this route only if it is new or shorter than the old one
            if cost_so_far[neighbor_index] == -1 or new_cost < cost_so_far[neighbor_index]:
                #save the new best cost g
                cost_so_far[neighbor_index] = new_cost
                #remember how we reached this neighbor
                came_from[neighbor_index] = current
                #calculate the priority f = g + h
                priority = new_cost + manhattan_distance(neighbor, goal)
                # add the neighbor to the priority queue
                heapq.heappush(priority_queue, (priority, new_cost, neighbor_index))

    #if the goal was never reached
    # MODIFIÉ : on renvoie un chemin vide au lieu de lever une erreur, pour que a_star() et backtracking() se comportent pareil vis-à-vis de main()
    if not explored_positions[n * n - 1]:
        return [], explored_positions

    #rebuild the path backwards: goal -> ... -> start
    # CONSERVÉ : contrairement au backtracking, la pile d'A* ne contient pas le chemin, il explore dans le désordre. D'où le tableau came_from
    path_positions = []
    current = n * n - 1
    while current != -1:
        path_positions.append(divmod(current, n))
        current = came_from[current]
    #put the path back in the normal order: start -> ... -> goal
    path_positions.reverse()

    return path_positions, explored_positions


###     [ SAVE SOLVED MAZE TO TEXT FILE ]

# MODIFIÉ : les questions à l'utilisateur vivent dans main(), pour que l'import de ce fichier reste silencieux

# AJOUTÉ : les deux solveurs demandés par le sujet, dans un seul fichier
ALGORITHMS = {'1': ('backtracking', backtracking), '2': ('a_star', a_star)}


def ask_algorithm():
    """Demande quel solveur utiliser."""
    while True:
        answer = input("Algorithme — 1 = backtracking, 2 = A* : ").strip()
        if answer in ALGORITHMS:
            return ALGORITHMS[answer]
        print("Répondre 1 ou 2.")


def ask_file_name(question):
    """Demande un nom de fichier. CONSERVÉ, règle du .txt comprise"""
    file_name = input(question)
    if not file_name.endswith(".txt"):
        file_name += ".txt"
    return file_name


def main():
    # File to solve
    input_file = ask_file_name("Entrer le nom du fichier labyrinthe à résoudre : ")
    algo_name, function = ask_algorithm()
    # saving solution in independant file
    output_file = ask_file_name("Entrer le nom du fichier pour le solveur : ")

    # Maze to ASCII
    # MODIFIÉ : read_maze() vient de grille.py. Elle renvoie aussi la taille, dont on déduit n, et elle écarte les lignes vides de fin de fichier
    grid, size = read_maze(input_file)

    path, visited = function(grid, size)

    # AJOUTÉ : un labyrinthe sans solution n'a rien à écrire
    if not path:
        print("No path found from start to goal.")
        return

    # AJOUTÉ : mark_solution() pose les '*' sur les cases explorées en vain, puis les 'o' sur le chemin final ET sur les ouvertures franchies — sans quoi le
    # tracé s'afficherait en pointillés
    mark_solution(grid, size, path, visited)
    write_maze(grid, size, output_file)

    print(f"Solution saved in {output_file} ({algo_name})")
    # AJOUTÉ : les deux chiffres qui serviront à la comparaison du chapitre 06
    print(f"Chemin : {len(path)} cases — explorées : {sum(visited)} cases")


# AJOUTÉ : rien ne s'exécute à l'import, pour que mesures.py puisse appeler backtracking() sans déclencher les questions
if __name__ == "__main__":
    main()
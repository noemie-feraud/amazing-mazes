from collections import deque

# Les 4 caractères du sujet, en codes numériques (ord('#') = 35, ord('.') = 46)
WALL, EMPTY = ord('#'), ord('.')
PATH, EXPLORED = ord('o'), ord('*')

# Haut, bas, gauche, droite
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def empty_grid(n):
    """Grille pleine, cases ouvertes, tous les murs debout. Renvoie (grid, size)"""
    # n couloirs + les n+1 murs qui les encadrent
    size = 2 * n + 1

    # On part d'un bloc plein et on creuse dedans
    grid = bytearray(b'#' * (size * size))

    # La case (i, j) s'écrit en (2i+1, 2j+1) : les cases sont aux indices impairs
    # La grille est plate, d'où l'index ligne * size + colonne
    for i in range(n):
        for j in range(n):
            grid[(2 * i + 1) * size + (2 * j + 1)] = EMPTY

    return grid, size

def open_entrance_exit(grid, size):
    """Ouvre l'entrée en haut à gauche et la sortie en bas à droite."""
    # Le coin, plus la bordure juste à côté : sinon le coin ne mène à rien
    grid[0] = EMPTY                                # coin (0, 0)
    grid[size] = EMPTY                             # (1, 0)
    grid[size * size - 1] = EMPTY                  # coin (2n, 2n)
    grid[(size - 2) * size + (size - 1)] = EMPTY   # (2n-1, 2n)
    # À appeler après la génération : ces ouvertures ne comptent pas dans les n*n - 1 murs cassés

def mark_solution(grid, size, path, visited):
    """Écrit 'o' sur le chemin et '*' sur les cases explorées pour rien."""
    n = (size - 1) // 2

    # Tableau indexé plutôt que "in path" : réponse immédiate au lieu de parcourir toute la liste à chaque case
    on_path = bytearray(n * n)
    for i, j in path:
        on_path[i * n + j] = 1

    # Les '*' d'abord, les 'o' ensuite : le chemin doit l'emporter
    for index in range(n * n):
        if visited[index] and not on_path[index]:
            i, j = divmod(index, n)
            grid[(2 * i + 1) * size + (2 * j + 1)] = EXPLORED

    previous = None
    for i, j in path:
        grid[(2 * i + 1) * size + (2 * j + 1)] = PATH
        if previous is not None:
            pi, pj = previous
            # Formule du milieu : le caractère entre deux cases voisines
            # Sans cette ligne, le chemin sort en pointillés
            grid[(i + pi + 1) * size + (j + pj + 1)] = PATH
        previous = (i, j)


def link_explored(grid, size):
    """Relie les '*' voisins. Utile avant un export image seulement"""
    n = (size - 1) // 2
    for i in range(n):
        for j in range(n):
            if grid[(2 * i + 1) * size + (2 * j + 1)] != EXPLORED:
                continue
            # Droite et bas seulement, sinon chaque paire est traitée 2 fois
            for ni, nj in ((i, j + 1), (i + 1, j)):
                if ni >= n or nj >= n:
                    continue
                middle = (i + ni + 1) * size + (j + nj + 1)
                # On ne remplace que du vide : ni un mur, ni un 'o'.
                if grid[middle] == EMPTY and \
                        grid[(2 * ni + 1) * size + (2 * nj + 1)] == EXPLORED:
                    grid[middle] = EXPLORED


def write_maze(grid, size, file_name):
    """Écrit la grille dans un fichier texte."""
    # 'wb' : la grille est déjà des octets, pas besoin de conversion
    with open(file_name, 'wb') as f:
        for r in range(size):
            # Ligne par ligne, pour ne pas garder une 2e copie en mémoire
            f.write(grid[r * size:(r + 1) * size])
            f.write(b'\n')


def read_maze(file_name):
    """Relit un fichier labyrinthe. Renvoie (grid, size)"""
    with open(file_name, 'rb') as f:
        lines = f.read().split(b'\n')
    lines = [line for line in lines if line]   # écarte la ligne vide finale

    # Sans ces 3 contrôles, un fichier abîmé plante beaucoup plus loin, avec un message incompréhensible
    if not lines:
        raise ValueError("The maze file is empty")
    width = len(lines[0])
    if any(len(line) != width for line in lines):
        raise ValueError("The maze must be rectangular")
    if width != len(lines):
        raise ValueError("The maze must be square")

    size = len(lines)
    return bytearray(b''.join(lines)), size


#LES TROIS CONTRÔLES DE VALIDITÉ 

# Réunis, ils prouvent qu'un labyrinthe est parfait
# Ils comparent à "!= WALL" et non "== EMPTY", pour rester valables sur un labyrinthe déjà résolu, qui contient des 'o' et des '*'

def all_cells_open(grid, size):
    """1. Aucune case n'a été oubliée par le générateur."""
    n = (size - 1) // 2
    return all(grid[(2 * i + 1) * size + (2 * j + 1)] != WALL
               for i in range(n) for j in range(n))

def count_broken_walls(grid, size):
    """2. Compte les murs intérieurs cassés. Doit valoir n*n - 1."""
    n = (size - 1) // 2
    total = 0
    for i in range(n):
        for j in range(n):
            # j+1 < n et i+1 < n : on ignore les bordures et l'entrée/sortie.
            if j + 1 < n and grid[(2 * i + 1) * size + (2 * j + 2)] != WALL:
                total += 1
            if i + 1 < n and grid[(2 * i + 2) * size + (2 * j + 1)] != WALL:
                total += 1
    return total
    # Plus que n*n - 1 : il y a une boucle. Moins : une région est isolée

def all_cells_reachable(grid, size):
    """3. Toutes les cases sont atteignables depuis (0, 0)."""
    n = (size - 1) // 2
    seen = bytearray(n * n)
    seen[0] = 1
    count = 1

    # Parcours en largeur. popleft() sort le plus ancien : premier arrivé, premier sorti FIFO
    queue = deque([(0, 0)])
    while queue:
        i, j = queue.popleft()
        for di, dj in DIRECTIONS:
            ni, nj = i + di, j + dj
            # On lit le mur entre les deux cases, pas la case voisine.
            if 0 <= ni < n and 0 <= nj < n and not seen[ni * n + nj] \
                    and grid[(i + ni + 1) * size + (j + nj + 1)] != WALL:
                seen[ni * n + nj] = 1
                count += 1
                queue.append((ni, nj))

    return count == n * n


def is_perfect(grid, size):
    """Les trois contrôles réunis. À lancer après chaque modif du générateur"""
    n = (size - 1) // 2
    return (all_cells_open(grid, size)
            and count_broken_walls(grid, size) == n * n - 1
            and all_cells_reachable(grid, size))
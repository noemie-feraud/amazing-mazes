import random

# AJOUTÉ : module commun décrit au chapitre 01 de la documentation.
# Il possède les constantes, la grille de départ, l'entrée/sortie et l'écritur du fichier, pour que le générateur et le solveur ne dupliquent jamais ce code
from grille import VIDE, grille_vide, ouvrir_entree_sortie, ecrire


###     [ INSTRUCTION 3: Perfect maze generation using Iterative Depth-First Search ]

# MODIFIÉ : la génération est maintenant dans une fonction, au lieu de s'exécuter
# au moment de l'import. Trois raisons :
#   - on peut l'appeler plusieurs fois dans le même programme (nécessaire à mesures.py)
#   - on peut la chronométrer et la tester automatiquement
#   - importer ce fichier ne déclenche plus aucune question à l'utilisateur
#
# MODIFIÉ : on manipule désormais des coordonnées de la grille LOGIQUE
# (i = ligne, j = colonne, de 0 à n-1), comme au chapitre 01, au lieu des
# coordonnées d'affichage avec un pas de 2. La conversion n'a lieu qu'au moment
# d'écrire dans la grille.

def backtracking(n, graine=None):
    """Génère un labyrinthe parfait et renvoie sa grille de caractères.

    n      : number of corridors (user input)
    graine : graine aléatoire. AJOUTÉ — à graine fixée, le même labyrinthe est
             rejoué à l'identique, ce qui est indispensable pour comparer deux
             solveurs sur le même labyrinthe et pour reproduire un bug.
    """
    # AJOUTÉ : générateur aléatoire privé plutôt que le module random global,
    # pour qu'une graine fixée ici ne puisse pas être perturbée ailleurs.
    rng = random.Random(graine)

    # MODIFIÉ : la grille pleine est construite par grille_vide() (chapitre 01).
    # Elle renvoie un bytearray de (2n+1)x(2n+1) murs dans lequel toutes les
    # cases-couloirs sont déjà ouvertes : il ne reste donc qu'à percer les murs
    # entre elles.
    grille, taille = grille_vide(n)  # grid size is always (2n + 1)

    # CONSERVÉ : une case est marquée dès qu'on l'atteint, jamais en sortant,
    # sinon le parcours pourrait revenir sur elle-même et boucler indéfiniment.
    visitees = bytearray(n * n)

    # Initialize starting point in the maze
    start_i, start_j = 0, 0
    visitees[start_i * n + start_j] = 1

    # MODIFIÉ : une liste simple remplace la deque. Une deque est faite pour les
    # files (rapide des deux côtés) ; une pile n'utilise qu'une extrémité, et
    # list.append / list.pop y sont légèrement plus rapides.
    pile = [(start_i, start_j)]

    # Main DFS loop (Depth-First Search)
    while len(pile) > 0:
        i, j = pile[-1]  # Peek at current top cell

        # Explore unvisited neighbors
        # CONSERVÉ : cette liste est reconstruite à chaque passage, et c'est essentiel. 
        # Un voisin peut être encore libre maintenant et déjà visité deux passages plus tard, 
        # creusé par une branche partie ailleurs. 
        # Si on ne construisait la liste qu'une seule fois, on finirait par percer un
        # mur vers une case déjà reliée : cela créerait un cycle et casserait la
        # propriété de labyrinthe parfait.
        # MODIFIÉ : les quatre directions sont écrites en clair plutôt que
        # parcourues dans une liste d'offsets — cela évite de créer un tuple et
        # de faire deux additions par direction, ce qui se voit sur une grille
        # d'un million de cases.
        candidats = []
        if i > 0 and not visitees[(i - 1) * n + j]:
            candidats.append((i - 1, j))
        if i + 1 < n and not visitees[(i + 1) * n + j]:
            candidats.append((i + 1, j))
        if j > 0 and not visitees[i * n + j - 1]:
            candidats.append((i, j - 1))
        if j + 1 < n and not visitees[i * n + j + 1]:
            candidats.append((i, j + 1))

        if len(candidats) > 0:
            # MODIFIÉ : rng.choice() remplace shuffle() + neighbors[0]
            # Résultat identique — une direction disponible tirée uniformément,
            # mais on ne mélange plus une liste de quatre éléments à chaque passage
            ni, nj = rng.choice(candidats)

            visitees[ni * n + nj] = 1

            # Break intermediate wall
            # MODIFIÉ : c'est la formule du milieu du chapitre 01. Le milieu de
            # (2i+1) et (2ni+1) vaut i+ni+1, et le même raisonnement vaut pour
            # les colonnes. Elle fonctionne indifféremment pour un mur vertical
            # et un mur horizontal, donc aucun if/else n'est nécessaire.
            # La case voisine, elle, est déjà ouverte.
            grille[(i + ni + 1) * taille + (j + nj + 1)] = VIDE

            pile.append((ni, nj))  # Push new cell onto stack
        else:
            pile.pop()  # Backtrack when hitting a dead end

    return grille, taille


###     [ INSTRUCTION 5: Perfect maze generation using Kruskal's algorithm ]

# Chapitre 03 de la documentation. Même sortie que backtracking() : une grille
# de caractères prête à écrire. Seule la façon de choisir les murs change.

def _representant(parent, x):
    """find() avec compression de chemin, en deux passes itératives."""
    # 1re passe : on remonte jusqu'au représentant de la région
    racine = x
    while parent[racine] != racine:
        racine = parent[racine]
    # 2e passe : on rattache tout le trajet directement à la racine
    # L'affectation simultanée mémorise l'ancien parent avant de l'écraser
    while parent[x] != racine:
        parent[x], x = racine, parent[x]
    return racine


def kruskal(n, graine=None):
    """Génère un labyrinthe parfait par fusion de régions (union-find).

    n      : number of corridors (user input)
    graine : même rôle que dans backtracking()
    """
    rng = random.Random(graine)
    grille, taille = grille_vide(n)  # grid size is always (2n + 1)

    # Liste de tous les murs intérieurs, encodés en entiers : 2*c pour le mur à
    # droite de la case c, 2*c+1 pour celui en dessous. Deux directions suffisent,
    # le mur à gauche d'une case étant le mur à droite de sa voisine.
    # Des entiers plutôt que des paires de tuples : ~20 fois moins de mémoire,
    # et il y en a près de 2 millions à n = 1000.
    murs = []
    for i in range(n):
        for j in range(n):
            c = i * n + j
            if j + 1 < n:
                murs.append(2 * c)
            if i + 1 < n:
                murs.append(2 * c + 1)

    # Le mélange remplace le tri par poids du Kruskal d'origine
    rng.shuffle(murs)

    # Au départ chaque case est sa propre région, donc son propre représentant
    # parent : une liste ordinaire, les valeurs vont jusqu'à n*n - 1
    # rang    : un bytearray suffit, l'union par rang garde les arbres très plats
    parent = list(range(n * n))
    rang = bytearray(n * n)
    restantes = n * n

    for mur in murs:
        # Décodage : quotient = la case, reste = mur en dessous (1) ou à droite (0)
        c, vertical = divmod(mur, 2)
        voisin = c + n if vertical else c + 1

        ra = _representant(parent, c)
        rb = _representant(parent, voisin)
        if ra == rb:
            continue  # déjà la même région : on garde le mur, sinon cycle

        # Union par rang : on accroche toujours le petit arbre sous le grand
        # L'échange évite d'écrire deux fois le même bloc
        if rang[ra] < rang[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rang[ra] == rang[rb]:
            rang[ra] += 1

        # Break intermediate wall — même formule du milieu que dans backtracking()
        i, j = divmod(c, n)
        ni, nj = divmod(voisin, n)
        grille[(i + ni + 1) * taille + (j + nj + 1)] = VIDE

        # Chaque fusion supprime une région. Quand il n'en reste qu'une, le
        # labyrinthe est complet : inutile de parcourir les murs restants.
        restantes -= 1
        if restantes == 1:
            break

    return grille, taille


###     [ INSTRUCTION 1: The user determines the size of the maze ]
###     [ INSTRUCTION 2: The user chooses the name of the output file ]

# MODIFIÉ : repris d'intro.py. Les questions vivent maintenant dans main(),
# pour que l'import de ce fichier reste silencieux.

def demander_taille():
    """Demande n tant que la réponse n'est pas un entier utilisable."""
    while True:
        # MODIFIÉ : int(input(...)) plantait sur un ValueError brut si la réponse
        # n'était pas un nombre, et le contrôle de taille affichait un message
        # mais laissait le programme continuer avec une variable inexistante.
        # Les deux cas sont traités ici.
        reponse = input("Define the size of the maze : ")
        try:
            taille = int(reponse)
        except ValueError:
            print("Merci d'entrer un nombre entier.")
            continue
        if taille <= 1:
            print("Choisir un entier supérieur à 1")
            continue
        return taille


def demander_algorithme():
    """Demande quel générateur utiliser."""
    while True:
        reponse = input("Algorithme — 1 = backtracking, 2 = kruskal : ").strip()
        if reponse in ALGORITHMES:
            return ALGORITHMES[reponse]
        print("Répondre 1 ou 2.")


def demander_fichier():
    """Demande le nom du fichier. CONSERVÉ d'intro.py, règle du .txt comprise."""
    nom_fichier = input("Définir un nom de fichier : ")
    if not nom_fichier.endswith(".txt"):
        nom_fichier += ".txt"
    return nom_fichier


###     [ INSTRUCTION 4: Open entrance at top-left and exit at bottom-right ]
###     [ SAVE AS ASCII TEXT FILE ]

# AJOUTÉ : les deux générateurs dans un seul fichier
ALGORITHMES = {'1': ('backtracking', backtracking), '2': ('kruskal', kruskal)}


def main():
    n = demander_taille()
    nom_algo, fonction = demander_algorithme()
    nom_fichier = demander_fichier()

    grille, taille = fonction(n)

    # Opening coordinates matching the subject page 3 example:
    # entrance at top-left corner, exit at bottom-right corner.
    # MODIFIÉ : les quatre ouvertures vivent maintenant dans
    # ouvrir_entree_sortie(), dans grille.py, parce que le solveur a besoin
    # exactement de la même convention.
    # On les applique APRÈS la génération : elles ne font pas partie de l'arbre
    # couvrant et ne doivent pas être comptées dans les n*n - 1 murs cassés.
    ouvrir_entree_sortie(grille, taille)

    # MODIFIÉ : ecrire() vient de grille.py. Elle écrit le bytearray ligne par
    # ligne en mode binaire, sans conversion en chaîne et sans garder une
    # seconde copie du labyrinthe en mémoire.
    ecrire(grille, taille, nom_fichier)

    print(f"Maze created in your file {nom_fichier} ({nom_algo})")


# AJOUTÉ : rien ne s'exécute si le fichier n'est pas lancé directement, pour que
# mesures.py et le solveur puissent importer backtracking() sans déclencher les
# questions.
if __name__ == '__main__':
    main()
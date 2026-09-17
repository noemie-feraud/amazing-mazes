from PIL import Image

from grille import WALL, EMPTY, PATH, EXPLORED

# Une couleur par caractère du sujet. Il n'y en a jamais d'autres
COLORS = {
    WALL:     (0, 0, 0),          # noir   : les murs
    EMPTY:    (245, 245, 235),    # blanc  : jamais visité
    EXPLORED: (20, 20, 160),      # bleu   : exploré pour rien
    PATH:     (190, 90, 200),     # violet : le chemin final
}


def export_image(grid, size, file_name, scale=1):
    """Écrit la grille en image, un caractère = scale x scale pixels."""
    # Table de traduction : pour chaque code de caractère, un numéro de couleur
    table = bytearray(256)
    palette = []
    for index, (code, color) in enumerate(COLORS.items()):
        table[code] = index
        palette.extend(color)
    # putpalette veut 256 couleurs de 3 composantes : on complète par des zéros
    palette.extend([0] * (768 - len(palette)))

    # translate() convertit toute la grille d'un coup, côté C C'est ici que le choix du bytearray paie : aucune boucle Python
    image = Image.frombytes('P', (size, size), bytes(grid.translate(bytes(table))))
    # Mode 'P' = palette : l'image stocke des numéros, pas des couleurs.
    image.putpalette(palette)

    if scale > 1:
        # NEAREST recopie le pixel tel quel. Les autres filtres lisseraient les murs et inventeraient des couleurs qui ne veulent rien dire
        image = image.resize((size * scale, size * scale), Image.NEAREST)

    # PIL choisit le format d'après l'extension. Préférer .png : le JPEG compresse avec pertes et bave autour des traits d'un pixel
    image.convert('RGB').save(file_name)


def ask_file_name(question, extension):
    """Demande un nom de fichier, ajoute l'extension si elle manque"""
    file_name = input(question)
    if not file_name.endswith(extension):
        file_name += extension
    return file_name


def main():
    from grille import read_maze

    input_file = ask_file_name("Fichier labyrinthe à convertir : ", ".txt")
    output_file = ask_file_name("Nom de l'image à créer : ", ".png")

    while True:
        answer = input("Taille d'un caractère en pixels (1 à 20) : ").strip()
        try:
            scale = int(answer)
        except ValueError:
            print("Merci d'entrer un nombre entier.")
            continue
        if not 1 <= scale <= 20:
            print("Choisir une valeur entre 1 et 20.")
            continue
        break

    grid, size = read_maze(input_file)
    export_image(grid, size, output_file, scale)

    print(f"Image saved in {output_file} ({size * scale}x{size * scale} pixels)")


if __name__ == '__main__':
    main()
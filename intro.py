import json

###   [ CONSIGNE 1 : L'utilisateur détermine la taille de la matrice du Lab ]      ###

taille_matrice = int(input("Definir la taille du labyrinthe : "))

# input l'utilisateur choisit un entier  N qui définit la taille de la matrice n*n

if taille_matrice <= 1:
    print("Choisir un entier supérieur à 1")
# on évite les erreurs si l'utilisateur choisit un entier inférieur ou égal à 1
else:
    lab = [["#" for n in range(taille_matrice)] for n in range(taille_matrice)]
# on set avec la matrice n*n rempli de # autant de fois que demandé

for ligne in lab:
    print(" ".join(ligne))
# join : colle les elements d une liste pour faire une seule str


###     [  CONSIGNE 2 : L' utilisateur crée son fichier json, le labyrinthe apparait dedans  ]      ###


# utilisateur choix nom de fichier

nom_fichier = input("Définir un nom de fichier ")
if not nom_fichier.endswith(".json"):
    nom_fichier += ".json"

lab_json = [" ".join(ligne) for ligne in lab]
# affichage pour json, transforme la liste en chaine texte

with open(nom_fichier, "w", encoding="utf-8") as f:
    json.dump(lab_json, f, ensure_ascii=False, indent=1)

print(f"Labyrinthe crée dans votre fichier {nom_fichier}")

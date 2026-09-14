import json

###   [ INSTRUCTION 1 : The user determines the size of the Lab matrix ]      ###

matrix_size = int(input("Define the size of the maze : "))

# input The user chooses an integer N which defines the size of the matrix

if matrix_size <= 1:
    print("Choisir un entier supérieur à 1")
# errors if the user chooses an integer less than or equal to 1
else:
    lab = [["#" for n in range(matrix_size)] for n in range(matrix_size)]
# set the matrix n*n fill with # as many forse as requested

for line in lab:
    print(" ".join(line))
# join : takes the elements of a list to make a single string


###     [  INSTRUCTION 2 : The user creates their TXT file, the maze appears in it  ]      ###


# User choose a filename

filename = input("Définir un nom de fichier ")
if not filename.endswith(".txt"):
    filename += ".txt"

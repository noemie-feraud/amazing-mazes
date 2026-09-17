import statistics
import sys
import time
import tracemalloc

from grille import is_perfect, open_entrance_exit
import generateur
import solveur

TAILLES = [100, 300, 600]
GRAINES = (0, 1, 2)


def valider(tailles):
    """Controle 1 : labyrinthes parfaits. Controle 2 : solveurs d'accord."""
    print("## Validation préalable\n")
    ok = True
    for nom_gen in ('backtracking', 'kruskal'):
        for n in tailles:
            grille, taille = getattr(generateur, nom_gen)(n, seed=0)
            parfait = is_perfect(grille, taille)
            open_entrance_exit(grille, taille)
            c1, _ = solveur.backtracking(grille, taille)
            c2, _ = solveur.a_star(grille, taille)
            identiques = c1 == c2
            ok = ok and parfait and identiques
            print(f"- {nom_gen} n={n} : parfait = {parfait}, "
                  f"chemins identiques = {identiques}")
    print(f"\n**Résultat global : {'tout est valide' if ok else 'ECHEC'}**\n")
    return ok


def mesurer_generation(tailles):
    print("## Génération : temps\n")
    print("| n | Backtracking | Kruskal | Rapport |")
    print("|---|---|---|---|")
    for n in tailles:
        moyennes = {}
        for nom_gen in ('backtracking', 'kruskal'):
            temps = []
            for graine in GRAINES:
                debut = time.perf_counter()
                getattr(generateur, nom_gen)(n, seed=graine)
                temps.append(time.perf_counter() - debut)
            moyennes[nom_gen] = statistics.mean(temps)
        rapport = moyennes['kruskal'] / moyennes['backtracking']
        print(f"| {n} | {moyennes['backtracking']:.2f} s | "
              f"{moyennes['kruskal']:.2f} s | {rapport:.1f}× |")
    print()


def mesurer_memoire(tailles):
    print("## Génération : pic mémoire\n")
    print("| n | Backtracking | Kruskal |")
    print("|---|---|---|")
    for n in tailles:
        pics = {}
        for nom_gen in ('backtracking', 'kruskal'):
            tracemalloc.start()
            getattr(generateur, nom_gen)(n, seed=0)
            _, pic = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            pics[nom_gen] = pic / 1e6
        print(f"| {n} | {pics['backtracking']:.1f} Mo | {pics['kruskal']:.1f} Mo |")
    print()


def mesurer_resolution(tailles):
    print("## Résolution\n")
    print("| Générateur | n | Chemin | Explorées BT | Explorées A* | "
          "Rapport A*/BT | Temps BT | Temps A* |")
    print("|---|---|---|---|---|---|---|---|")
    for nom_gen in ('backtracking', 'kruskal'):
        for n in tailles:
            longueurs, expl_bt, expl_as, t_bt, t_as = [], [], [], [], []
            for graine in GRAINES:
                grille, taille = getattr(generateur, nom_gen)(n, seed=graine)
                open_entrance_exit(grille, taille)

                debut = time.perf_counter()
                chemin_bt, vus_bt = solveur.backtracking(grille, taille)
                t_bt.append(time.perf_counter() - debut)

                debut = time.perf_counter()
                chemin_as, vus_as = solveur.a_star(grille, taille)
                t_as.append(time.perf_counter() - debut)

                longueurs.append(len(chemin_bt))
                expl_bt.append(sum(vus_bt))
                expl_as.append(sum(vus_as))

            m = statistics.mean
            rapport = m(expl_as) / m(expl_bt)
            print(f"| {nom_gen} | {n} | {m(longueurs):.0f} | {m(expl_bt):.0f} | "
                  f"{m(expl_as):.0f} | {rapport:.2f} | {m(t_bt):.2f} s | "
                  f"{m(t_as):.2f} s |")
    print()


def mesurer_proportion(tailles):
    print("## Part du labyrinthe occupée par la solution\n")
    print("| Générateur | n | Chemin | % des cases | % explorées |")
    print("|---|---|---|---|---|")
    for nom_gen in ('backtracking', 'kruskal'):
        for n in tailles:
            grille, taille = getattr(generateur, nom_gen)(n, seed=0)
            open_entrance_exit(grille, taille)
            chemin, vus = solveur.backtracking(grille, taille)
            print(f"| {nom_gen} | {n} | {len(chemin)} | "
                  f"{100 * len(chemin) / (n * n):.1f} % | "
                  f"{100 * sum(vus) / (n * n):.1f} % |")
    print()


def main():
    tailles = [int(a) for a in sys.argv[1:]] or TAILLES
    print(f"# Mesures — tailles {tailles}, graines {list(GRAINES)}\n")
    if not valider(tailles):
        print("Mesures interrompues : corriger les algorithmes d'abord.")
        return
    mesurer_generation(tailles)
    mesurer_memoire(tailles)
    mesurer_resolution(tailles)
    mesurer_proportion(tailles)


if __name__ == '__main__':
    main()
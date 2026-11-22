######################################################################
#                Projet 1 - Chats et souris - QR Corp                #
#                          Constantes du jeu                         #
######################################################################

# Tout est dessiné dans un espace "virtuel" de 1600 x 900 (format 16/9).
# Cet espace est ensuite mis à l'échelle pour tenir dans la fenêtre réelle.
LARG = 1600  # Largeur virtuelle (16/9)
HAUT = 900   # Hauteur virtuelle (16/9)

BACKGROUND_COLOR = "#A9A9A9"  # Gris clair : fond du jeu + bandes de remplissage
CONSOLE_COLOR = "#FFFFFF"     # Blanc pur : fond de la console

# Zones de l'écran, en pixels virtuels : (x0, y0, x1, y1) = coin haut-gauche, coin bas-droit
# Disposition modifiée par rapport à la maquette pour privilégier le plateau de jeu.
ZONE_JEU = (100, 50, 900, 850)          # plateau de jeu (à gauche)
ZONE_SELECTION = (1000, 50, 1550, 400)  # éditeur / sélection des cartes (en haut à droite)
ZONE_CONSOLE = (1000, 550, 1550, 850)   # ligne de commande + messages (en bas à droite)

# Couleurs des cartes, en hexadécimal.
# D'abord les 8 couleurs prioritaires (composantes 0 ou 255, les plus distinctes),
# puis toutes les combinaisons RVB avec des composantes 0, 127 ou 255 (27 couleurs), puis un gris clair : 28 couleurs au total.
COULEURS = [
    "#000000",  # noir
    "#FFFFFF",  # blanc
    "#FF0000",  # R : rouge
    "#00FF00",  # G : vert
    "#0000FF",  # B : bleu
    "#FFFF00",  # RG : jaune
    "#00FFFF",  # GB : cyan
    "#FF00FF",  # RB : magenta
]
NIVEAUX = ["00", "7F", "FF"]  # 0, 127 et 255 écrits en hexadécimal
for r in range(3):
    for g in range(3):
        for b in range(3):
            couleur = "#" + NIVEAUX[r] + NIVEAUX[g] + NIVEAUX[b]
            if couleur not in COULEURS:
                COULEURS.append(couleur)
del r, g, b, couleur  # on retire les variables de boucle : seule COULEURS doit rester
COULEURS.append("#D3D3D3")  # gris clair (ajouté à la fin pour ne pas décaler les autres indices)

AFFICHE_REPERE = False  # True : affiche le repère de coordonnées (aide au développement) — mettre False pour la démo

BACKGROUND_COLOR = COULEURS[27]   # Gris clair : fond du jeu + bandes de remplissage
CONSOLE_COLOR = COULEURS[1]
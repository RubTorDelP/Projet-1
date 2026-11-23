######################################################################
#                Projet 1 - Chats et souris - QR Corp                #
######################################################################

# Organisation du fichier, en 3 blocs :
#   1. MANIPULATION   : les données (grille, sélection, commandes) - aucun pixel
#   2. ÉCRAN VIRTUEL  : géométrie et dessin dans l'espace virtuel 1600 x 900
#   3. ÉCRAN RÉEL     : conversion virtuel <-> fenêtre réelle
# puis le programme principal.

import fltk
from constant import (LARG, HAUT, BACKGROUND_COLOR, CONSOLE_COLOR, ZONE_JEU, ZONE_SELECTION,
                      ZONE_CONSOLE, AFFICHE_REPERE, COULEURS)

taille_ecran = (1600, 900)  # Taille de la fenêtre au départ (largeur, hauteur) en pixels réels


######################################################################
######################################################################
###                        1. MANIPULATION                         ###
######################################################################
######################################################################
# Les données du jeu et les fonctions qui les modifient. Ne dessine rien, ne connaît aucun pixel.

#--Variables-------------------
taille = 5                  # Nombre de lignes et de colonnes de la grille

# Grille du jeu : tableau de tableaux d'éléments.
# Un élément = [couleur, image, info]
#   couleur : indice dans COULEURS (ou None = case vide, pas encore de carte)
#   image   : "c" (chat), "s" (souris) ou None (rien)
#   info    : indice dans COULEURS de la petite bulle d'aide du joueur (ou None = pas de bulle)
grille = [[[None, None, None] for col in range(taille)] for li in range(taille)]

# Zone de sélection : grille 3 x 3
#   1re colonne : les symboles à placer ("X" = vide, "S" = souris, "C" = chat)
#   2 autres colonnes : les couleurs, à partir de COULEURS[1] (blanc), ligne par ligne
selection_symboles = ["X", "S", "C"]

# Ce que le joueur a choisi dans la zone de sélection
symbole_choisi = None   # "X", "S" ou "C" (None = rien choisi)
couleur_choisie = None  # indice dans COULEURS (None = rien choisi)
console_choisie = False # True quand la console est sélectionnée (les autres sélections sont alors retirées)

# Ligne de commande
saisie = ""                       # texte en cours de saisie dans la console
message_console = ("", "black")   # dernier message affiché dans la console : (texte, couleur)
#------------------------------


def clic_jeu(li, col):
    """
    entrée 1 : li (int) ligne de la case cliquée sur le plateau
    entrée 2 : col (int) colonne de la case cliquée sur le plateau

    action : applique la sélection à la case :
             - couleur choisie : change la couleur de la case
             - symbole choisi  : change l'image de la case (X efface)

    sortie 1 : (str) message à afficher dans la console
    """
    if symbole_choisi is None and couleur_choisie is None:
        return "Choisissez un symbole ou une couleur"
    element = grille[li][col]
    if couleur_choisie is not None:
        element[0] = couleur_choisie
    if symbole_choisi is not None:
        element[1] = {"X": None, "S": "s", "C": "c"}[symbole_choisi]
    return f"Case ({li}, {col}) modifiée"


def execute_commande(ligne):
    """
    entrée 1 : ligne (str) commande tapée dans la console

    action : exécute la commande : nouvelle [n] (grille vide, n = taille actuelle si absent), aide

    sortie 1 : (str) message à afficher
    sortie 2 : (str) couleur du message ("black" ou "red")
    """
    global grille, taille
    mots = ligne.split()
    if not mots:
        return "", "black"
    commande, arguments = mots[0].lower(), mots[1:]

    if commande == "aide":
        return "nouvelle [n] | aide", "black"

    if commande == "nouvelle":
        if arguments:                                 # nouvelle n : change la taille
            if not arguments[0].isdigit() or int(arguments[0]) < 3:
                return "Nombre de couleurs invalide (entier >= 3)", "red"
            taille = int(arguments[0])
        grille = [[[None, None, None] for c in range(taille)] for l in range(taille)]  # grille vide (sans n : taille actuelle)
        return f"Nouvelle grille : {taille} couleurs", "black"

    return "Commande inconnue : tapez aide", "red"


def touche_console(touche):
    """
    entrée 1 : touche (str) nom de la touche appuyée (fltk.touche)

    action : Entrée exécute la commande, Retour arrière efface, sinon ajoute le caractère à la saisie

    sortie : aucune
    """
    global saisie, message_console
    speciales = {"space": " ", "underscore": "_", "minus": "-", "period": "."}
    if touche == "Return":
        message_console = execute_commande(saisie)   # (texte, couleur) affiché en bas de la console
        saisie = ""
    elif touche == "BackSpace":
        saisie = saisie[:-1]
    elif touche in speciales:
        saisie += speciales[touche]
    elif len(touche) == 1:                            # lettre ou chiffre
        saisie += touche


######################################################################
######################################################################
###                        2. ÉCRAN VIRTUEL                        ###
######################################################################
######################################################################
# Géométrie et dessin, en coordonnées VIRTUELLES (1600 x 900). Passe par le bloc 3 pour la fenêtre.

derniere_souris = None  # dernière position connue de la souris (pixels réels), pour détecter le survol


#--Géométrie des grilles et des zones--------------------------------------

def taille_cellule(x0, y0, x1, y1, nombre):
    """
    entrée 1 : x0 (float) abscisse du coin haut-gauche de la zone
    entrée 2 : y0 (float) ordonnée du coin haut-gauche de la zone
    entrée 3 : x1 (float) abscisse du coin bas-droit de la zone
    entrée 4 : y1 (float) ordonnée du coin bas-droit de la zone
    entrée 5 : nombre (int) nombre de lignes et de colonnes de la grille

    action : calcule la taille d'une case d'une grille carrée qui tient dans la zone

    sortie 1 : (float) taille d'une case, en pixels virtuels
    """
    return min(x1 - x0, y1 - y0) / nombre


def case_grille(x0, y0, x1, y1, nombre, li, col):
    """
    entrée 1 : x0 (float) abscisse du coin haut-gauche de la zone
    entrée 2 : y0 (float) ordonnée du coin haut-gauche de la zone
    entrée 3 : x1 (float) abscisse du coin bas-droit de la zone
    entrée 4 : y1 (float) ordonnée du coin bas-droit de la zone
    entrée 5 : nombre (int) nombre de lignes et de colonnes de la grille
    entrée 6 : li (int) ligne de la case
    entrée 7 : col (int) colonne de la case

    action : calcule les coins de la case (li, col) de la grille

    sortie 1 : (float) ax, abscisse du coin haut-gauche de la case (virtuel)
    sortie 2 : (float) ay, ordonnée du coin haut-gauche de la case (virtuel)
    sortie 3 : (float) bx, abscisse du coin bas-droit de la case (virtuel)
    sortie 4 : (float) by, ordonnée du coin bas-droit de la case (virtuel)
    """
    t = taille_cellule(x0, y0, x1, y1, nombre)
    gx, gy = coin_grille(x0, y0, x1, y1, nombre)
    return gx + col * t, gy + li * t, gx + (col + 1) * t, gy + (li + 1) * t


def case_de(x, y, x0, y0, x1, y1, nombre):
    """
    entrée 1 : x (float) abscisse virtuelle du point
    entrée 2 : y (float) ordonnée virtuelle du point
    entrée 3 : x0 (float) abscisse du coin haut-gauche de la zone
    entrée 4 : y0 (float) ordonnée du coin haut-gauche de la zone
    entrée 5 : x1 (float) abscisse du coin bas-droit de la zone
    entrée 6 : y1 (float) ordonnée du coin bas-droit de la zone
    entrée 7 : nombre (int) nombre de lignes et de colonnes de la grille

    action : cherche la case de la grille qui contient le point

    sortie 1 : (tuple ou None) (li, col) de la case, ou None si le point est hors de la grille
    """
    t = taille_cellule(x0, y0, x1, y1, nombre)
    gx, gy = coin_grille(x0, y0, x1, y1, nombre)
    col = int((x - gx) // t)
    li = int((y - gy) // t)
    if 0 <= li < nombre and 0 <= col < nombre:
        return li, col
    return None


def coin_grille(x0, y0, x1, y1, nombre):
    """
    entrée 1 : x0 (float) abscisse du coin haut-gauche de la zone
    entrée 2 : y0 (float) ordonnée du coin haut-gauche de la zone
    entrée 3 : x1 (float) abscisse du coin bas-droit de la zone
    entrée 4 : y1 (float) ordonnée du coin bas-droit de la zone
    entrée 5 : nombre (int) nombre de lignes et de colonnes de la grille

    action : calcule le coin haut-gauche de la grille (centrée si la zone n'est pas carrée)

    sortie 1 : (float) gx, abscisse du coin haut-gauche de la grille (virtuel)
    sortie 2 : (float) gy, ordonnée du coin haut-gauche de la grille (virtuel)
    """
    cote = nombre * taille_cellule(x0, y0, x1, y1, nombre)
    gx = x0 + ((x1 - x0) - cote) / 2
    gy = y0 + ((y1 - y0) - cote) / 2
    return gx, gy


def dans_grille(x, y):
    """
    entrée 1 : x (float) abscisse virtuelle
    entrée 2 : y (float) ordonnée virtuelle

    action : teste si le point est dans la grille du plateau
             (bord droit et bord bas exclus, sinon on obtiendrait une case qui n'existe pas)

    sortie 1 : (bool) True si le point est dans la grille, False sinon
    """
    gx, gy = coin_grille(*ZONE_JEU, taille)
    cote = taille * taille_cellule(*ZONE_JEU, taille)
    return gx <= x < gx + cote and gy <= y < gy + cote


def get_column(x):
    """
    entrée 1 : x (float) abscisse virtuelle (axe horizontal)

    action : calcule la colonne du plateau qui correspond à x

    sortie 1 : (int) numéro de colonne
    """
    gx, gy = coin_grille(*ZONE_JEU, taille)
    return int((x - gx) // taille_cellule(*ZONE_JEU, taille))


def get_line(y):
    """
    entrée 1 : y (float) ordonnée virtuelle (axe vertical)

    action : calcule la ligne du plateau qui correspond à y

    sortie 1 : (int) numéro de ligne
    """
    gx, gy = coin_grille(*ZONE_JEU, taille)
    return int((y - gy) // taille_cellule(*ZONE_JEU, taille))


def pixels_vers_ref(x, y):
    """
    entrée 1 : x (float) abscisse dans la FENÊTRE (ex : un clic)
    entrée 2 : y (float) ordonnée dans la FENÊTRE

    action : convertit le pixel en case du plateau

    sortie 1 : (int ou None) ligne, ou None si hors de la grille
    sortie 2 : (int ou None) colonne, ou None si hors de la grille
    """
    xv, yv = vers_virtuel(x, y)
    if not dans_grille(xv, yv):
        return None, None
    return get_line(yv), get_column(xv)


def centre_cellules(li, col):
    """
    entrée 1 : li (int) ligne de la case
    entrée 2 : col (int) colonne de la case

    action : calcule le centre de la case du plateau

    sortie 1 : (float) abscisse virtuelle du centre
    sortie 2 : (float) ordonnée virtuelle du centre
    """
    taille_cel = taille_cellule(*ZONE_JEU, taille)
    gx, gy = coin_grille(*ZONE_JEU, taille)
    return gx + taille_cel * col + taille_cel / 2, gy + taille_cel * li + taille_cel / 2


def zone_de(x, y):
    """
    entrée 1 : x (float) abscisse virtuelle
    entrée 2 : y (float) ordonnée virtuelle

    action : cherche dans quelle zone de l'écran se trouve le point

    sortie 1 : (str ou None) "jeu", "selection", "console", ou None si aucune zone
    """
    zones = {"jeu": ZONE_JEU, "selection": ZONE_SELECTION, "console": ZONE_CONSOLE}
    for nom, (x0, y0, x1, y1) in zones.items():
        if x0 <= x < x1 and y0 <= y < y1:
            return nom
    return None


def mouse_action(ev):
    """
    entrée 1 : ev (événement fltk ou None) renvoyé par fltk.donne_ev()

    action : analyse la souris (clic gauche ou déplacement) et trouve la zone et la case pointées

    sortie 1 : (str ou None) action : "clique", "survole" ou None
    sortie 2 : (tuple) (x, y, zone, case) :
               x, y : position en pixels VIRTUELS
               zone : "jeu", "selection", "console" ou None
               case : (li, col) dans la grille du jeu ou de la sélection, ou None
    """
    global derniere_souris
    if fltk.type_ev(ev) == "ClicGauche":
        xr, yr = fltk.abscisse(ev), fltk.ordonnee(ev)
        action = "clique"
    else:
        xr, yr = fltk.abscisse_souris(), fltk.ordonnee_souris()
        action = "survole" if (xr, yr) != derniere_souris else None
    derniere_souris = (xr, yr)

    x, y = vers_virtuel(xr, yr)
    zone = zone_de(x, y)
    case = None
    if zone == "jeu":
        case = case_de(x, y, *ZONE_JEU, taille)
    elif zone == "selection":
        case = case_de(x, y, *ZONE_SELECTION, 3)
    return action, (x, y, zone, case)


#--Dessin------------------------------------------------------------------

def show_repere(grad=100, sous_grad=20):
    """
    entrée 1 : grad (int) distance virtuelle entre deux graduations principales (avec valeur affichée)
    entrée 2 : sous_grad (int) distance virtuelle entre deux graduations secondaires

    action : affiche un repère de coordonnées VIRTUELLES (0 à 1600, 0 à 900) sur la zone 16/9 ;
             il suit la mise à l'échelle, donc les valeurs lues sont celles à utiliser dans le code

    sortie : aucune
    """
    for v in range(0, max(LARG, HAUT) + 1, sous_grad):
        principale = v % grad == 0
        couleur = "#505050" if principale else "#C8C8C8"
        if v <= LARG:   # ligne verticale x = v
            ax, ay = vers_ecran(v, 0)
            bx, by = vers_ecran(v, HAUT)
            fltk.ligne(ax, ay, bx, by, couleur=couleur, tag="repere")
            if principale:
                fltk.texte(ax + 2, ay + 2, str(v), couleur=couleur, taille=taille_police(12), tag="repere")
        if v <= HAUT:   # ligne horizontale y = v
            ax, ay = vers_ecran(0, v)
            bx, by = vers_ecran(LARG, v)
            fltk.ligne(ax, ay, bx, by, couleur=couleur, tag="repere")
            if principale and v > 0:
                fltk.texte(ax + 2, ay + 2, str(v), couleur=couleur, taille=taille_police(12), tag="repere")


def rectangle_zone(zone, couleur="black", remplissage="", epaisseur=2):
    """
    entrée 1 : zone (tuple) (x0, y0, x1, y1) en pixels virtuels
    entrée 2 : couleur (str) couleur du contour
    entrée 3 : remplissage (str) couleur de l'intérieur ("" = vide)
    entrée 4 : epaisseur (float) épaisseur du contour, en pixels virtuels

    action : dessine le rectangle de la zone, mis à l'échelle

    sortie : aucune
    """
    ax, ay = vers_ecran(zone[0], zone[1])
    bx, by = vers_ecran(zone[2], zone[3])
    fltk.rectangle(ax, ay, bx, by, couleur=couleur, remplissage=remplissage,
                   epaisseur=max(1, epaisseur * echelle()))


def show_grid(x0, y0, x1, y1, nombre):
    """
    entrée 1 : x0 (float) abscisse du coin haut-gauche de la zone
    entrée 2 : y0 (float) ordonnée du coin haut-gauche de la zone
    entrée 3 : x1 (float) abscisse du coin bas-droit de la zone
    entrée 4 : y1 (float) ordonnée du coin bas-droit de la zone
    entrée 5 : nombre (int) nombre de lignes et de colonnes

    action : dessine les lignes d'une grille carrée de nombre x nombre cases dans la zone
             (sert pour le plateau de jeu et pour la zone de sélection)

    sortie : aucune
    """
    taille_cel = taille_cellule(x0, y0, x1, y1, nombre)
    gx, gy = coin_grille(x0, y0, x1, y1, nombre)
    cote = nombre * taille_cel
    for i in range(nombre + 1):
        #----Lignes verticales
        ax, ay = vers_ecran(gx + i * taille_cel, gy)
        bx, by = vers_ecran(gx + i * taille_cel, gy + cote)
        fltk.ligne(ax, ay, bx, by, couleur='blue')
        #----Lignes horizontales
        ax, ay = vers_ecran(gx, gy + i * taille_cel)
        bx, by = vers_ecran(gx + cote, gy + i * taille_cel)
        fltk.ligne(ax, ay, bx, by, couleur='blue')


def dessine_element(li, col, element):
    """
    entrée 1 : li (int) ligne de la case du plateau
    entrée 2 : col (int) colonne de la case du plateau
    entrée 3 : element (list) [couleur, image, info]

    action : dessine l'élément dans la case :
             - couleur : remplit la case (None = case vide, blanche)
             - image   : lettre C ou S dans un rond blanc, au centre
             - info    : petit cercle de couleur dans le coin haut-gauche

    sortie : aucune
    """
    couleur, image, info = element
    taille_cel = taille_cellule(*ZONE_JEU, taille)
    xc, yc = centre_cellules(li, col)          # centre de la case (virtuel)
    demi = taille_cel / 2

    #---Fond de la case
    remplissage = "#FFFFFF" if couleur is None else COULEURS[couleur]
    ax, ay = vers_ecran(xc - demi, yc - demi)
    bx, by = vers_ecran(xc + demi, yc + demi)
    fltk.rectangle(ax, ay, bx, by, couleur=remplissage, remplissage=remplissage)

    #---Image : C ou S dans un rond blanc
    if image is not None:
        xe, ye = vers_ecran(xc, yc)
        r = taille_cel * 0.3 * echelle()
        fltk.cercle(xe, ye, r, couleur="black", remplissage="white", epaisseur=max(1, 2 * echelle()))
        fltk.texte(xe, ye, image.upper(), taille=taille_police(taille_cel * 0.3), ancrage="center")

    #---Info : petit cercle dans le coin haut-gauche
    if info is not None:
        xe, ye = vers_ecran(xc - demi * 0.65, yc - demi * 0.65)
        r = taille_cel * 0.1 * echelle()
        fltk.cercle(xe, ye, r, couleur="black", remplissage=COULEURS[info])


def show_cords(x, y):
    """
    entrée 1 : x (int) abscisse à afficher
    entrée 2 : y (int) ordonnée à afficher

    action : affiche les coordonnées en haut de la console

    sortie : aucune
    """
    xe, ye = vers_ecran(ZONE_CONSOLE[0] + 20, ZONE_CONSOLE[1] + 20)
    fltk.texte(xe, ye, f"coord : ({x}, {y})", taille=taille_police(18), tag="coord")
    fltk.mise_a_jour()


def show_refs(li, col):
    """
    entrée 1 : li (int) ligne de la case
    entrée 2 : col (int) colonne de la case

    action : affiche la ligne et la colonne de la case dans la console, en rouge

    sortie : aucune
    """
    xe, ye = vers_ecran(ZONE_CONSOLE[0] + 20, ZONE_CONSOLE[1] + 60)
    fltk.texte(xe, ye, f"case : ({li}, {col})", taille=taille_police(18), couleur="red", tag="ref")
    fltk.mise_a_jour()


def dessine_base():
    """
    entrée : aucune

    action : efface tout, dessine le fond gris et les bandes, puis le repère si AFFICHE_REPERE

    sortie : aucune
    """
    fltk.efface_tout()
    dessine_fond()
    if AFFICHE_REPERE:
        show_repere()


def dessine_zone_jeu():
    """
    entrée : aucune

    action : dessine les éléments de la grille du plateau, puis les lignes de la grille par-dessus

    sortie : aucune
    """
    for li in range(taille):
        for col in range(taille):
            dessine_element(li, col, grille[li][col])
    x0, y0, x1, y1 = ZONE_JEU
    show_grid(x0, y0, x1, y1, taille)


def dessine_zone_selection():
    """
    entrée : aucune

    action : dessine la grille 3 x 3 de la sélection (symboles X, S, C puis couleurs)
             et encadre en noir ce qui est choisi

    sortie : aucune
    """
    x0, y0, x1, y1 = ZONE_SELECTION
    t = taille_cellule(x0, y0, x1, y1, 3)
    for li in range(3):
        #---1re colonne : symbole
        ax, ay, bx, by = case_grille(x0, y0, x1, y1, 3, li, 0)
        xe, ye = vers_ecran((ax + bx) / 2, (ay + by) / 2)
        fltk.texte(xe, ye, selection_symboles[li], taille=taille_police(t * 0.4), ancrage="center")

        #---2 autres colonnes : couleurs
        for col in range(1, 3):
            numero = 1 + li * 2 + (col - 1)           # 1, 2 sur la 1re ligne ; 3, 4 ; puis 5, 6
            ax, ay, bx, by = case_grille(x0, y0, x1, y1, 3, li, col)
            pa, pb = vers_ecran(ax, ay), vers_ecran(bx, by)
            fltk.rectangle(pa[0], pa[1], pb[0], pb[1], couleur=COULEURS[numero], remplissage=COULEURS[numero])

    show_grid(x0, y0, x1, y1, 3)                      # les lignes de la grille par-dessus

    #---Encadre en noir le symbole et la couleur choisis
    for li in range(3):
        for col in range(3):
            choisi = (col == 0 and selection_symboles[li] == symbole_choisi) or \
                     (col > 0 and 1 + li * 2 + (col - 1) == couleur_choisie)
            if choisi:
                rectangle_zone(case_grille(x0, y0, x1, y1, 3, li, col), couleur="black", epaisseur=6)


def dessine_console():
    """
    entrée : aucune

    action : dessine la console (rectangle blanc, cadre épais si sélectionnée),
             la ligne de saisie en haut et le dernier message en bas

    sortie : aucune
    """
    epaisseur = 6 if console_choisie else 2
    rectangle_zone(ZONE_CONSOLE, remplissage=CONSOLE_COLOR, epaisseur=epaisseur)

    #---Ligne de saisie, en haut (le "_" montre où l'on écrit quand la console est sélectionnée)
    curseur = "_" if console_choisie else ""
    xe, ye = vers_ecran(ZONE_CONSOLE[0] + 20, ZONE_CONSOLE[1] + 20)
    fltk.texte(xe, ye, "> " + saisie + curseur, taille=taille_police(18), police="Courier")

    #---Dernier message, en bas
    texte, couleur = message_console
    xe, ye = vers_ecran(ZONE_CONSOLE[0] + 20, ZONE_CONSOLE[3] - 20)
    fltk.texte(xe, ye, texte, couleur=couleur, taille=taille_police(18), ancrage="sw")


def redessine():
    """
    entrée : aucune

    action : redessine tout l'écran (base, zone de jeu, sélection, console)

    sortie : aucune
    """
    dessine_base()
    dessine_zone_jeu()
    dessine_zone_selection()
    dessine_console()
    fltk.mise_a_jour()


######################################################################
######################################################################
###                         3. ÉCRAN RÉEL                          ###
######################################################################
######################################################################
# Seul bloc qui connaît la taille RÉELLE de la fenêtre : conversion virtuel <-> fenêtre.

def echelle():
    """
    entrée : aucune

    action : calcule le facteur de zoom entre l'espace virtuel 1600 x 900 et la fenêtre réelle
             (le plus petit des deux rapports, pour que la zone 16/9 tienne entière)

    sortie 1 : (float) facteur d'échelle
    """
    return min(fltk.largeur_fenetre() / LARG, fltk.hauteur_fenetre() / HAUT)


def origine():
    """
    entrée : aucune

    action : calcule où commence la zone 16/9 dans la fenêtre, pour qu'elle soit centrée
             (l'espace restant forme les bandes)

    sortie 1 : (float) ox, abscisse du coin haut-gauche de la zone 16/9 dans la fenêtre
    sortie 2 : (float) oy, ordonnée du coin haut-gauche de la zone 16/9 dans la fenêtre
    """
    e = echelle()
    ox = (fltk.largeur_fenetre() - LARG * e) / 2
    oy = (fltk.hauteur_fenetre() - HAUT * e) / 2
    return ox, oy


def vers_ecran(x, y):
    """
    entrée 1 : x (float) abscisse virtuelle
    entrée 2 : y (float) ordonnée virtuelle

    action : convertit un point virtuel en point de la fenêtre réelle (pour dessiner)

    sortie 1 : (float) abscisse dans la fenêtre
    sortie 2 : (float) ordonnée dans la fenêtre
    """
    e = echelle()
    ox, oy = origine()
    return ox + x * e, oy + y * e


def vers_virtuel(x, y):
    """
    entrée 1 : x (float) abscisse dans la fenêtre (ex : un clic)
    entrée 2 : y (float) ordonnée dans la fenêtre

    action : convertit un point de la fenêtre réelle en point virtuel

    sortie 1 : (float) abscisse virtuelle
    sortie 2 : (float) ordonnée virtuelle
    """
    e = echelle()
    ox, oy = origine()
    return (x - ox) / e, (y - oy) / e


def taille_police(t):
    """
    entrée 1 : t (float) taille de police prévue pour l'espace virtuel

    action : met la taille de police à l'échelle de la fenêtre (au moins 1)

    sortie 1 : (int) taille de police à utiliser
    """
    return max(1, int(t * echelle()))


def dessine_fond():
    """
    entrée : aucune

    action : remplit toute la fenêtre avec BACKGROUND_COLOR
             (même couleur pour le fond du jeu et les bandes : un seul rectangle suffit)

    sortie : aucune
    """
    fltk.rectangle(0, 0, fltk.largeur_fenetre(), fltk.hauteur_fenetre(),
                   couleur=BACKGROUND_COLOR, remplissage=BACKGROUND_COLOR)


######################################################################
######################################################################
###                      PROGRAMME PRINCIPAL                       ###
######################################################################
######################################################################
# Boucle des événements : souris, clavier, redimensionnement.

#---Programme principal--------------

if __name__ == "__main__":
    fltk.cree_fenetre(taille_ecran[0], taille_ecran[1], redimension=True)  # fenêtre de départ, redimensionnable
    redessine()                                       # au départ : grille vide (cases blanches)

    while True:
        ev = fltk.donne_ev()                          # ne bloque pas : None s'il n'y a pas d'événement
        typeEv = fltk.type_ev(ev)

        if typeEv == "Redimension":                   # la taille de la fenêtre a changé
            redessine()                               # tout est recalculé à la nouvelle échelle
        elif typeEv == "Quitte":
            break

        action, (x, y, zone, case) = mouse_action(ev)
        if action == "clique":
            if zone == "console":
                #---Clic dans la console : la sélectionne (ou la désélectionne si elle l'était déjà) ;
                #   la sélectionner retire le symbole et la couleur choisis
                console_choisie = not console_choisie
                if console_choisie:
                    symbole_choisi = None
                    couleur_choisie = None
                redessine()
            elif zone == "selection" and case is not None:
                #---Clic dans la sélection : 1re colonne = symbole, sinon couleur ;
                #   recliquer sur ce qui est déjà choisi le retire ; désélectionne la console
                li, col = case
                console_choisie = False
                if col == 0:
                    symbole = selection_symboles[li]
                    symbole_choisi = None if symbole_choisi == symbole else symbole
                else:
                    couleur = 1 + li * 2 + (col - 1)    # indice dans COULEURS : 1, 2 / 3, 4 / 5, 6
                    couleur_choisie = None if couleur_choisie == couleur else couleur
                redessine()
            elif zone == "jeu" and case is not None:
                message_console = (clic_jeu(*case), "black")  # affiché en bas de la console
                redessine()

        if typeEv == "Touche" and console_choisie:   # clavier : seulement si la console est sélectionnée
            touche_console(fltk.touche(ev))
            redessine()

        fltk.mise_a_jour()                            # rafraîchit l'affichage (et règle la vitesse de la boucle)

    fltk.ferme_fenetre()

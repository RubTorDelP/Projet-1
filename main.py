#----------------------------------------------------------------------
#------------------------------Importation-----------------------------
#----------------------------------------------------------------------

import fltk


#----------------------------------------------------------------------
#------------------------------Constante-------------------------------
#----------------------------------------------------------------------


TAILLE_ECRAN = (1600, 900)  
RATIO = 16 / 9              

LARG = TAILLE_ECRAN[0]
HAUT = LARG / RATIO

#----------------------------------------------------------------------
#------------------------------variable global--------------------------------
#----------------------------------------------------------------------

echelle = 1           
origine = (0, 0)     

taille = 5                        # nombre de cases par ligne du plateau
zone_plateau = (100, 50, 900, 850)  # (x0, y0, x1, y1) du plateau, en coordonnées virtuelles
plateau = [[0 for col in range(taille)] for li in range(taille)]  # 0 = vide, 1 = chat, 2 = souris
type_placement = "Chat"           # ce que le clic pose : "Chat", "Souris" ou "Vide"


#----------------------------------------------------------------------
#-----------------------------Redimensionnement------------------------
#----------------------------------------------------------------------

def vers_ecran(x, y):
    """
    action : convertit un point virtuel en point de la fenêtre (pour dessiner)
    """
    ox, oy = origine
    return ox + x * echelle, oy + y * echelle


def vers_virtuel(x, y):
    """
    action : convertit un point de la fenêtre en point virtuel
    """
    ox, oy = origine
    return (x - ox) / echelle, (y - oy) / echelle


#----------------------------------------------------------------------
#--------------------------Fonction Dessiner---------------------------
#----------------------------------------------------------------------

def affiche_grille(x0, y0, x1, y1, nombre, couleur="black"):
    """
    nombre : nb de carre par ligne
    """
    cote = min(x1 - x0, y1 - y0)          # la grille est carrée : on prend le plus petit côté
    t = cote / nombre                     # taille d'un carré
    gx = x0 + (x1 - x0 - cote) / 2        # coin haut-gauche de la grille (centrée)
    gy = y0 + (y1 - y0 - cote) / 2
    for i in range(nombre + 1):
        ax, ay = vers_ecran(gx + i * t, gy)          # ligne verticale
        bx, by = vers_ecran(gx + i * t, gy + cote)
        fltk.ligne(ax, ay, bx, by, couleur=couleur)
        ax, ay = vers_ecran(gx, gy + i * t)          # ligne horizontale
        bx, by = vers_ecran(gx + cote, gy + i * t)
        fltk.ligne(ax, ay, bx, by, couleur=couleur)


def affiche_image(x0, y0, x1, y1, fichier):
    ax, ay = vers_ecran(x0, y0)
    bx, by = vers_ecran(x1, y1)
    fltk.image((ax + bx) / 2, (ay + by) / 2, fichier,largeur=max(1, int(bx - ax)), hauteur=max(1, int(by - ay)), ancrage="center")


def affiche_texte(x, y, texte, taille, couleur="black"):
    xe, ye = vers_ecran(x, y)
    fltk.texte(xe, ye, texte, couleur=couleur, taille=max(1, int(taille * echelle)))


def case_de(x, y, x0, y0, x1, y1, nombre):
    """
    renvoie la case (li, col) de la grille qui contient le point virtuel (x, y),
    ou None si le point est hors de la grille
    (même calcul que affiche_grille ; remplace dans_grille, get_lines, get_column et pixels_vers_ref)
    """
    cote = min(x1 - x0, y1 - y0)
    t = cote / nombre
    gx = x0 + (x1 - x0 - cote) / 2
    gy = y0 + (y1 - y0 - cote) / 2
    col = int((x - gx) // t)
    li = int((y - gy) // t)
    if 0 <= li < nombre and 0 <= col < nombre:
        return li, col
    return None


def coins_case(li, col, x0, y0, x1, y1, nombre):
    """
    renvoie (ax, ay, bx, by), les coins virtuels de la case (li, col) de la grille
    (remplace centre_cellules : pratique pour affiche_image)
    """
    cote = min(x1 - x0, y1 - y0)
    t = cote / nombre
    gx = x0 + (x1 - x0 - cote) / 2
    gy = y0 + (y1 - y0 - cote) / 2
    return gx + col * t, gy + li * t, gx + (col + 1) * t, gy + (li + 1) * t


def affiche_plateau(plateau, x0, y0, x1, y1):
    """
    affiche l'image du chat ou de la souris dans chaque case du plateau qui en contient un
    """
    images = {1: "images/cat.png", 2: "images/mouse.png"}
    nombre = len(plateau)
    for li in range(nombre):
        for col in range(nombre):
            if plateau[li][col] in images:
                affiche_image(*coins_case(li, col, x0, y0, x1, y1, nombre), images[plateau[li][col]])




#----------------------------------------------------------------------
#----------------------------Manipulation------------------------------
#----------------------------------------------------------------------

#manip du jeu

def modifie_plateau(plateau, li, col, type_placement):
    """
    action : met dans la case (li, col) du plateau : 1 pour "Chat", 2 pour "Souris", 0 sinon
             (repris de update_plateau, avec plateau[li][col] dans le bon ordre)
    """
    if type_placement == "Chat":
        plateau[li][col] = 1
    elif type_placement == "Souris":
        plateau[li][col] = 2
    else:
        plateau[li][col] = 0





#----------------------------------------------------------------------
#----------------------------Dessine tout------------------------------
#----------------------------------------------------------------------

def dessine_tout():
    """
    zone de dessin pour afficher tout
    prend en entre 
    """
    fltk.efface_tout()
    fltk.rectangle(0, 0, fltk.largeur_fenetre(), fltk.hauteur_fenetre(),couleur="#D3D3D3", remplissage="#D3D3D3")
    affiche_grille(*zone_plateau, taille)

    #---Images du plateau : chat ou souris dans chaque case qui en contient un
    images = {1: "images/chat.png", 2: "images/souris.png"}
    for li in range(taille):
        for col in range(taille):
            if plateau[li][col] in images:
                affiche_image(*coins_case(li, col, *zone_plateau, taille), images[plateau[li][col]])

    fltk.mise_a_jour()





#----------------------------------------------------------------------
#------------------------------main--------------------------------
#----------------------------------------------------------------------

if __name__ == "__main__":
    fltk.cree_fenetre(TAILLE_ECRAN[0], TAILLE_ECRAN[1], redimension=True)
    dessine_tout()

    while True:
        ev = fltk.attend_ev()
        typeEv = fltk.type_ev(ev)

        if typeEv == "Quitte":                 
            break

        elif typeEv == "Redimension":          
            echelle = min(fltk.largeur_fenetre() / LARG, fltk.hauteur_fenetre() / HAUT)
            origine = (fltk.largeur_fenetre() - LARG * echelle) / 2, (fltk.hauteur_fenetre() - HAUT * echelle) / 2
            dessine_tout()




        elif typeEv == "ClicGauche":           
            x, y = vers_virtuel(fltk.abscisse(ev), fltk.ordonnee(ev))
            case = case_de(x, y, *zone_plateau, taille)
            if case is not None:                       # clic dans le plateau
                li, col = case
                modifie_plateau(plateau, li, col, type_placement)
                dessine_tout()
    fltk.ferme_fenetre()
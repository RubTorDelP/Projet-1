
#----------------------------------------------------------------------
#------------------------------Importation-----------------------------
#----------------------------------------------------------------------

import fltk
import pickle

#----------------------------------------------------------------------
#------------------------------Constantes-------------------------------
#----------------------------------------------------------------------

TAILLE_ECRAN = (1600, 900)
RATIO = 16 / 9

LARG = TAILLE_ECRAN[0]
HAUT = LARG / RATIO


#----------------------------------------------------------------------
#------------------------------Variables globales-----------------------
#----------------------------------------------------------------------

echelle = 1
origine = (0, 0)

taille = 5

zone_plateau = (100, 50, 900, 850)
zone_plateau_selec = (1100, 50, 1600, 500)
zone_commande = (975, 550, 1550, 850)


# Chaque case contient (type_piece, couleur)
# 0 = vide, 1 = chat, 2 = souris

plateau = [[(0, None) for col in range(taille)] for li in range(taille)]
#plateau = [ [(0, "magenta"), (2, "red"), (0, "yellow"), (1, "yellow"), (0, "green")], [(2, "magenta"), (0, "blue"), (0, "yellow"), (0, "blue"), (1, "green")], [(0, "red"), (1, "blue"), (0, "red"), (0, "yellow"), (2, "yellow")], [(1, "magenta"), (0, "blue"), (2, "green"), (0, "magenta"), (0, "green")], [(0, "green"), (0, "red"), (1, "red"), (2, "blue"), (0, "magenta")], ]
plateau_selec = [[(0, None) for col in range(3)] for li in range(3)]

plateau_selec[0][0] = (1, "red")
plateau_selec[1][0] = (2, "blue")

type_placement = "Chat"
couleur_placement = None


#commande
commande = ""
commande_retour = ""
commande_retour_couleur = "black"


#----------------------------------------------------------------------
#-----------------------------Redimensionnement-------------------------
#----------------------------------------------------------------------

def vers_ecran(x, y):
    ox, oy = origine
    return ox + x * echelle, oy + y * echelle


def vers_virtuel(x, y):
    ox, oy = origine
    return (x - ox) / echelle, (y - oy) / echelle


#----------------------------------------------------------------------
#--------------------------Fonctions de dessin--------------------------
#----------------------------------------------------------------------

def affiche_grille(x0, y0, x1, y1, nombre, couleur="black"):

    cote = min(x1 - x0, y1 - y0)
    t = cote / nombre

    gx = x0 + (x1 - x0 - cote) / 2
    gy = y0 + (y1 - y0 - cote) / 2

    for i in range(nombre + 1):

        ax, ay = vers_ecran(gx + i * t, gy)
        bx, by = vers_ecran(gx + i * t, gy + cote)

        fltk.ligne(ax, ay, bx, by, couleur=couleur)

        ax, ay = vers_ecran(gx, gy + i * t)
        bx, by = vers_ecran(gx + cote, gy + i * t)

        fltk.ligne(ax, ay, bx, by, couleur=couleur)


def affiche_image(x0, y0, x1, y1, fichier):

    ax, ay = vers_ecran(x0, y0)
    bx, by = vers_ecran(x1, y1)

    fltk.image(
        (ax + bx) / 2,
        (ay + by) / 2,
        fichier,
        largeur=max(1, int(bx - ax)),
        hauteur=max(1, int(by - ay)),
        ancrage="center"
    )


def affiche_texte(x, y, texte, taille, couleur="black"):

    xe, ye = vers_ecran(x, y)

    fltk.texte(
        xe, ye, texte,
        couleur=couleur,
        taille=max(1, int(taille * echelle))
    )


def affiche_plateau(plateau, x0, y0, x1, y1):

    images = {
        1: "images/cat.png",
        2: "images/mouse.png"
    }

    nombre = len(plateau)

    for li in range(nombre):
        for col in range(nombre):

            type_piece, couleur = plateau[li][col]

            if type_piece in images:

                if couleur is not None:
                    fltk.rectangle(
                        *[vers_ecran(x, y) for x, y in [
                            coins_case(li, col, x0, y0, x1, y1, nombre)[:2],
                            coins_case(li, col, x0, y0, x1, y1, nombre)[2:]
                        ]],
                        remplissage=couleur
                    )

                affiche_image(
                    *coins_case(li, col, x0, y0, x1, y1, nombre),
                    images[type_piece]
                )
#----------------------------------------------------------------------
#------------------------sauvegarder et charger-------------------------
#----------------------------------------------------------------------
def sauvegarde(cle,val):
    '''
    meme propriete que un dico mais non supprimer lors de la fin du programme
    entre : prend une cle et une donnée
    sortie: modifie le dico
    '''


    import pickle
    try:
        with open("data", "rb") as fichier:
            dico = pickle.load(fichier)
    except:
        reset()
        with open("data", "rb") as fichier:
            dico = pickle.load(fichier)

    dico[cle] = val
    with open("data", "wb") as fichier:
        pickle.dump(dico, fichier)


def charge(cle):
    """
    meme propriete que un dico mais non supprimer lors de la fin du programme
    entre: prend une cle
    sortie: retourne la valeur de la cle
    """
    import pickle
    with open("data", "rb") as fichier:
        dico = pickle.load(fichier)
    
    return dico[cle]



def charge_tout():
    """ 
    meme propriete que un dico mais non supprimer lors de la fin du programme
    sortie: le dico entier
    """
    import pickle
    with open("data", "rb") as fichier:
        dico = pickle.load(fichier)
    return dico

def reset():
    """
    meme propriete que un dico mais non supprimer lors de la fin du programme
    sortie: rend le dico vide
    """
    import pickle
    with open("data", "wb") as fichier:
        pickle.dump({}, fichier)


#----------------------------------------------------------------------
#----------------------------Manipulation------------------------------
#----------------------------------------------------------------------
def verif_plateau(plateau):
    """
    Pas de case sans couleur (None)
    Pas deux chats sur une meme ligne ou colonne
    Pas deux souris sur une meme ligne ou colonne
    entree : le plateau (liste de listes de (type_piece, couleur))
    sortie : True si le plateau respecte les regles, False sinon
    """
    n = len(plateau)

   # Verification des cases sans couleur
    for li in range(n):
        for col in range(n):
            if plateau[li][col][1] is None:
                return False

    for piece in (1, 2):  # 1 = chat, 2 = souris
        for i in range(n):
            nb_ligne = sum(1 for col in range(n) if plateau[i][col][0] == piece)
            nb_colonne = sum(1 for li in range(n) if plateau[li][i][0] == piece)

            if nb_ligne > 1 or nb_colonne > 1:
                return False

            


    return True

def case_de(x, y, x0, y0, x1, y1, nombre):

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

    cote = min(x1 - x0, y1 - y0)
    t = cote / nombre

    gx = x0 + (x1 - x0 - cote) / 2
    gy = y0 + (y1 - y0 - cote) / 2

    return (
        gx + col * t,
        gy + li * t,
        gx + (col + 1) * t,
        gy + (li + 1) * t
    )


def chosir_type_placement(x, y):

    global type_placement, couleur_placement

    case = case_de(x, y, *zone_plateau_selec, 3)

    if case is not None:

        li, col = case

        # Colonne 0 : type de pièce
        if col == 0 and li == 0:
            type_placement = "Chat"

        elif col == 0 and li == 1:
            type_placement = "Souris"

        elif col == 0 and li == 2:
            type_placement = "Vide"
            couleur_placement = None

        # Colonnes 1 et 2 : les 5 couleurs
        elif col == 1 and li == 0:
            couleur_placement = "red"

        elif col == 2 and li == 0:
            couleur_placement = "blue"

        elif col == 1 and li == 1:
            couleur_placement = "green"

        elif col == 2 and li == 1:
            couleur_placement = "yellow"

        elif col == 1 and li == 2:
            couleur_placement = None

        # Dernière case : pas de couleur
        elif col == 2 and li == 2:
            couleur_placement = "magenta"


def modifie_plateau(plateau, li, col, type_placement):

    if type_placement == "Chat":
        plateau[li][col] = (1, couleur_placement)

    elif type_placement == "Souris":
        plateau[li][col] = (2, couleur_placement)

    elif type_placement == "Vide":
        plateau[li][col] = (0, couleur_placement)



def touche_commande(touche):
    """
    ajoute la touche à la commande, Retour arrière efface, Entrée affiche la commande dans la console puis la vide
    """
    global commande
    if touche == "Return":
        execution_commande(commande)
        print("commande :", commande)
        commande = ""
    elif touche == "BackSpace":
        commande = commande[:-1]
    elif touche == "space":
        commande = commande + " "
    elif len(touche) == 1:
        commande = commande + touche



def execution_commande(txt):
    """
    execute la commande 
    """

    global plateau, taille, commande_retour, commande_retour_couleur

    commande = txt.split()

    if not commande:                                  
        return

    if commande[0] == "charger":
        if len(commande) == 1:
            commande_retour = "Error: veuiller entre un nom pour le plateau a charger"
            commande_retour_couleur = "red"
        else:
            try:
                plateau = charge(commande[1])
                taille = len(plateau)
                commande_retour = "charger :" + commande[1] + " avec succes"
                commande_retour_couleur = "green"
            except (FileNotFoundError, KeyError):
                commande_retour = "Error: plateau introuvable : " + commande[1]
                commande_retour_couleur = "red"


    elif commande[0] == "sauvegarder":
        if len(commande) == 1:
            commande_retour = "Error: veuiller entre un nom pour le plateau"
            commande_retour_couleur = "red"
        else:
            sauvegarde(commande[1], plateau)
            commande_retour = "sauvegarder :" + commande[1] + " avec succes"
            commande_retour_couleur = "green"

    elif commande[0] == "nouvelle":
        if len(commande) == 1 or not(commande[1].isdigit()) or int(commande[1]) == 0:
            plateau = [[(0, None) for col in range(taille)] for li in range(taille)]
            commande_retour = "nouvelle carte de taille : " + str(taille)
        else:
            taille = int(commande[1])
            plateau = [[(0, None) for col in range(taille)] for li in range(taille)]
            commande_retour = "nouvelle carte de taille : " + str(taille)
            commande_retour_couleur = "green"

    elif commande[0] == "resetall":
        reset()
        taille = 5
        plateau = [[(0, None) for col in range(taille)] for li in range(taille)]
        commande_retour = "le fichier de sauvgarder a ete reinstialise "
        commande_retour_couleur = "black"

    elif commande[0] == "verifier":
        if verif_plateau(plateau):
            commande_retour = "plateau valide!"
            commande_retour_couleur = "green"
        else:
            commande_retour = "plateau invalide!"
            commande_retour_couleur = "red"


    elif commande[0] == "aide":
        commande_retour_couleur = "black"
        commande_retour = "charger <nom>|sauvegarder <nom>|nouvelle [n]|verifier|aide|resetall"
        


    else:
        commande_retour_couleur = "red"
        commande_retour = "commande inconnue: " + commande[0]



#----------------------------------------------------------------------
#----------------------------Dessine tout-------------------------------
#----------------------------------------------------------------------

def dessine_tout():

    fltk.efface_tout()

    fltk.rectangle(
        0, 0,
        fltk.largeur_fenetre(),
        fltk.hauteur_fenetre(),
        couleur="#D3D3D3",
        remplissage="#D3D3D3"
    )

    affiche_grille(*zone_plateau, taille)
    affiche_grille(*zone_plateau_selec, 3)

    images = {
        1: "images/cat.png",
        2: "images/mouse.png"
    }

    #--- Plateau principal

    for li in range(taille):
        for col in range(taille):

            type_piece, couleur = plateau[li][col]

            ax, ay, bx, by = coins_case(
                li, col, *zone_plateau, taille
            )

            # Afficher la couleur de fond, même sans pièce
            if couleur is not None:

                ax_e, ay_e = vers_ecran(ax, ay)
                bx_e, by_e = vers_ecran(bx, by)

                fltk.rectangle(
                    ax_e, ay_e, bx_e, by_e,
                    remplissage=couleur
                )

            # Afficher l'image uniquement si une pièce existe
            if type_piece in images:

                affiche_image(
                    ax, ay, bx, by,
                    images[type_piece]
                )

    #--- Plateau de sélection

    for li in range(3):
        for col in range(3):

            ax, ay, bx, by = coins_case(
                li, col, *zone_plateau_selec, 3
            )

            ax_e, ay_e = vers_ecran(ax, ay)
            bx_e, by_e = vers_ecran(bx, by)

            # Fond par défaut
            couleur_fond = "#D3D3D3"

            # Dernière ligne blanche
            if li == 2 and (col == 1 or col == 0):
                couleur_fond = "white"

            # Cases de couleur
            elif col == 1 and li == 0:
                couleur_fond = "red"
                

            elif col == 2 and li == 0:
                couleur_fond = "blue"

            elif col == 1 and li == 1:
                couleur_fond = "green"

            elif col == 2 and li == 1:
                couleur_fond = "yellow"

            elif col == 2 and li == 2:
                couleur_fond = "magenta"

            fltk.rectangle(
                ax_e, ay_e, bx_e, by_e,
                remplissage=couleur_fond
            )

            # Images des pièces
            if col == 0 and li == 0:
                affiche_image(
                    ax, ay, bx, by,
                    images[1]
                )

            elif col == 0 and li == 1:
                affiche_image(
                    ax, ay, bx, by,
                    images[2]
                )

            # Cases vides colorées : troisième colonne
            elif col == 2 and li == 0:
                pass

            elif col == 2 and li == 1:
                pass

    # Texte Vide centré sur la dernière ligne
    ax, ay, bx, by = coins_case(
        2, 1, *zone_plateau_selec, 3
    )

    ax_e, ay_e = vers_ecran(ax, ay)
    bx_e, by_e = vers_ecran(bx, by)

    fltk.texte(
        (ax_e + bx_e) / 2,
        (ay_e + by_e) / 2,
        "Vide",
        taille=25,
        ancrage="center"
    )

    #zone de commande 
    x0, y0 = vers_ecran(zone_commande[0], zone_commande[1])
    x1, y1 = vers_ecran(zone_commande[2], zone_commande[3])
    fltk.rectangle(x0, y0, x1, y1, couleur="black", remplissage="white")
    affiche_texte(zone_commande[0] + 20, zone_commande[1] + 20, "> " + commande, 15)
    
    affiche_texte(zone_commande[0] + 20, zone_commande[1] + 50, commande_retour, 15,commande_retour_couleur)
    






    fltk.mise_a_jour()
    
#------------------------------------ ---------------------------------
#------------------------------Main-------------------------------------
#----------------------------------------------------------------------

if __name__ == "__main__":

    fltk.cree_fenetre(
        TAILLE_ECRAN[0],
        TAILLE_ECRAN[1],
        redimension=True
    )

    dessine_tout()

    while True:

        ev = fltk.attend_ev()
        typeEv = fltk.type_ev(ev)

        if typeEv == "Quitte":
            break

        elif typeEv == "Redimension":
            #plateau = [ [(0, "magenta"), (2, "red"), (0, "yellow"), (1, "yellow"), (0, "green")], [(2, "magenta"), (0, "blue"), (0, "yellow"), (0, "blue"), (1, "green")], [(0, "red"), (1, "blue"), (0, "red"), (0, "yellow"), (2, "yellow")], [(1, "magenta"), (0, "blue"), (2, "green"), (0, "magenta"), (0, "green")], [(0, "green"), (0, "red"), (1, "red"), (2, "blue"), (0, "magenta")], ]
            
            print(plateau)
            echelle = min(
                fltk.largeur_fenetre() / LARG,
                fltk.hauteur_fenetre() / HAUT
            )

            origine = (
                (fltk.largeur_fenetre() - LARG * echelle) / 2,
                (fltk.hauteur_fenetre() - HAUT * echelle) / 2
            )

            dessine_tout()

        elif typeEv == "ClicGauche":

            x, y = vers_virtuel(
                fltk.abscisse(ev),
                fltk.ordonnee(ev)
            )

            # Clic dans le plateau de sélection

            case = case_de(
                x, y,
                *zone_plateau_selec,
                3
            )

            if case is not None:
                chosir_type_placement(x, y)

            else:

                # Clic dans le plateau principal

                case = case_de(
                    x, y,
                    *zone_plateau,
                    taille
                )

                if case is not None:

                    li, col = case

                    modifie_plateau(
                        plateau,
                        li,
                        col,
                        type_placement
                    )
            dessine_tout()

        elif typeEv == "Touche":
            touche_commande(fltk.touche(ev))
            
            
            dessine_tout()

    fltk.ferme_fenetre()
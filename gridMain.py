######################################################################
#                        AP1 - 2024 - TP fltk                        #
######################################################################

import fltk

#--Constantes------------------
LARG = 800 #Largeur de la fenêtre
HAUT = 600 #Hauteur de la fenêtre
TAILLE = 8 #Nombre de lignes et de colonnes de la grille
TAILLE_CEL = 50 #Taille d'une cellule en pixels
X_OFFSET = 100 # décallage gauche - min 30 pour afficher les références
Y_OFFSET = 50 # décallage droite - min 30
#------------------------------

def show_cadres_textes():
    """
    Construit les cadres pour l'affichage des coordonnées d'un pixel et des références d'une cellule
    """
    #---Cadre pour afficher les coordonnées d'un pixel
    fltk.texte(fltk.largeur_fenetre() - 200, 100, "coord :", taille = 12)
    fltk.rectangle(fltk.largeur_fenetre() - 210, 80, fltk.largeur_fenetre() - 20, 150)
    
    #---Cadre pour afficher les références d'une cellule
    fltk.texte(fltk.largeur_fenetre() - 200, 200, "refs :", taille = 12, couleur = 'red')
    fltk.rectangle(fltk.largeur_fenetre() - 210, 180, fltk.largeur_fenetre() - 20, 250, couleur = 'red')


def show_grid(nb_cel, taille_cel, x_offset, y_offset):
    """
    Affiche une grille carrée avec des marques de repérage.
    
    :param nb_cel: (int) nombre de colonnes et nombre de cellules par ligne
    :param taille_cel: (int) taille d'une cellule en pixels
    :param x_offset: (int) décalage, en pixels, par rapport au bord gauche de la fenêtre
    :param y_offset: (int) décalage, en pixels, par rapport au bord supérieur de la fenêtre
    
    :return: None
    """
    x, y = 10, 10 #position du coi

    
    for i in range(nb_cel + 1) :
        #----Affichage des lignes
        fltk.ligne(x_offset + i*taille_cel, y_offset, x_offset + i*taille_cel, y_offset + nb_cel*taille_cel, couleur = 'blue')
        fltk.ligne(x_offset, y_offset + i*taille_cel, x_offset + nb_cel*taille_cel, y_offset + i*taille_cel, couleur = 'blue')


def show_cords(x,y):
    fltk.texte((590+780)//2- 5, (90+150)//2, f"({x},{y})", taille = 12, tag="coord")
    fltk.mise_a_jour()

def show_refs(li, col):
    fltk.texte( (590+780)//2 - 5, (180+250)//2, f"({li}, {col})",  taille = 12, tag="ref")
    fltk.mise_a_jour()
    
def dans_grille(x,y, TAILLE, TAILLE_CEL, X_OFFSET, Y_OFFSET):
    coins = [(X_OFFSET, Y_OFFSET),
             (X_OFFSET+(+TAILLE*TAILLE_CEL), Y_OFFSET),
             (X_OFFSET, TAILLE*TAILLE_CEL),
             (X_OFFSET+(TAILLE*TAILLE_CEL), Y_OFFSET + (TAILLE*TAILLE_CEL))]
    
    return x >= coins[0][0] and x <= coins[3][0] and y >= coins[0][1] and y <= coins[3][1]

def get_lines(x, X_OFFSET, TAILLE_CEL):
    x = x-X_OFFSET
    x = x//TAILLE_CEL
    return x

def get_column(y, Y_OFFSET, TAILLE_CEL):
    y = y-Y_OFFSET
    y = y//TAILLE_CEL
    return y
    
def pixels_vers_ref(x,y, TAILLE_CEL, X_OFFSET, Y_OFFSET):
    if not dans_grille(x,y, TAILLE, TAILLE_CEL, X_OFFSET, Y_OFFSET):
        return None, None
    else:
        return get_lines(x, X_OFFSET, TAILLE_CEL), get_column(y, Y_OFFSET, TAILLE_CEL)

def centre_cellules(col, li):
    coins = [((X_OFFSET+TAILLE_CEL*col), (Y_OFFSET+TAILLE_CEL*li)),
            ((X_OFFSET+TAILLE_CEL*(col+1)), (Y_OFFSET+TAILLE_CEL*li)),
            ((X_OFFSET+TAILLE_CEL*col), (Y_OFFSET+TAILLE_CEL*(li+1))),
            ((X_OFFSET+TAILLE_CEL*(col+1)), (Y_OFFSET+TAILLE_CEL*(li+1)))]
    
    centre = ((coins[0][0] + coins[1][0])//2, ((coins[0][1] + coins[2][1])//2))
    return centre
    
#---Programme principal--------------

if __name__ == "__main__":

    fltk.cree_fenetre(LARG, HAUT)
    fltk.repere(50) # Affichage d'un repère
    
    show_grid(TAILLE, TAILLE_CEL, X_OFFSET, Y_OFFSET)
    show_cadres_textes()
    while True:
        ev = fltk.attend_ev()
        typeEv = fltk.type_ev(ev)
        if typeEv == "ClicGauche":
            x = fltk.abscisse(ev)
            y = fltk.ordonnee(ev)
            fltk.efface("coord")
            fltk.efface("ref")
            show_cords(x,y)
            li, col = pixels_vers_ref(x, y,TAILLE_CEL, X_OFFSET, Y_OFFSET)
            if li is not None and col is not None:
                show_refs(li, col)
            else:
                fltk.efface("ref")
            if li is not None and col is not None:
                radius = TAILLE*0.1
                xc, yc = centre_cellules(li, col)
                fltk.cercle(xc,yc, radius, remplissage="blue", tag="cercle")
            
        elif typeEv == "Quitte":
            fltk.ferme_fenetre()
        elif typeEv == "ClicDroit":
            fltk.efface("cercle")
    

    
    
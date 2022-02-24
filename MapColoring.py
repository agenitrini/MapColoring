
import cv2
from tkinter import *
from tkinter.filedialog import askopenfilename
#import random
import time
import sys
import os
import pickle


def neighbours(pt):
    x, y = pt
    L = []
    for i in [-1, 1]:
        L.append((x + i, y))
    for j in [-1, 1]:
        L.append((x, y + j))
    return L


def area(pt):
    global Out, image
    
    S = set()  # zone
    FS = set()  # frontière zone
    DejaTraites = {f for f in Out}
    DejaVus = {pt}
    L = [pt]
    i = 0
    while i < len(L):
        pt = L[i]
        i += 1
        if pt not in DejaTraites:
            (b, g, r) = image[pt[1], pt[0]]
            DejaTraites.add(pt)

            if (r, g, b) != (255, 255, 255) and (r, g, b) != (0, 0, 0):
                image[pt[1], pt[0]] = (0, 0, 0)
                (r, g, b) = (0, 0, 0)
                
            if (r, g, b) != (0, 0, 0):
                S.add(pt)
                for n in neighbours(pt):
                    if n not in DejaVus:
                        L.append(n)
                        DejaVus.add(n)
            else:
                FS.add(pt)
                
    return S, FS


def allareas():
    global WIDTH, HEIGHT, image, In, Zones, FZones, Graphe
    
    E = {e for e in In}
    Zones = []
    FZones = []
    while len(E) > 0:
        N = []
        pt = E.pop()
        (b, g, r) = image[pt[1], pt[0]]
        while len(E)>0 and (r, g, b) == (0, 0, 0):
            N.append(pt)
            pt = E.pop()
            (b, g, r) = image[pt[1], pt[0]]
        for n in N:
            E.add(n)
##        x, y = pt
##        image[y-2:y+2, x-2:x+2] = (0,0,255)
##        cv2.imshow('Carte', image)
##        cv2.waitKey(0)
        S, FS = area(pt)
        
##        remplir(S, None, (255,0,0))
##        remplir(FS, None, (0,0,255))
##        cv2.imshow('Carte', image)
##        cv2.waitKey(0)       
        
        E = E - (S | FS)
        if len(S) > 0:
            Zones.append(S)
            FZones.append(FS)
        print(len(E))
        ### a nettoyer par la suite
        if len(E)<10:
            print(E)
    print('fini', len(Zones), [len(z) for z in Zones], [len(z) for z in FZones])
    Graphe = voisins()

##    for i in range(len(Graphe)):
##        color(Zones[i], i, (211, 211, 211))
##    for i in [random.randint(0, len(Graphe)-1)]:
##        remplir(Zones[i], i, (0, 0, 255))
##        for j in range(len(Graphe[i])):
##            color(Zones[Graphe[i][j]], None, (255, 0, 0))
    return None


def gravite(S):
    x = 0
    y = 0
    for s in S:
        x += s[0]
        y += s[1]
    return x//len(S), y//len(S)


        
def remplir(S, i, col):
    global image
    
    for x, y in S:
        image[y, x] = col

    if i != None:
        font                   = cv2.FONT_HERSHEY_PLAIN
        bottomLeftCornerOfText = (x, y)
        fontScale              = 1.5
        fontColor              = (0,0,0)
        thickness              = 1
        lineType               = 2

        cv2.putText(image,str(i), 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)

    return None

    


def color(S, i, col):
    global image
    
    x, y = gravite(S)
    #image[y-5:y+6, x-5:x+6] = col

    if i != None:
        font                   = cv2.FONT_HERSHEY_PLAIN
        bottomLeftCornerOfText = (x-10, y+15)
        fontScale              = 1.5
        fontColor              = (0,0,0)
        thickness              = 1
        lineType               = 2

        cv2.putText(image,str(i), 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)

    return None


def sontvoisins(F, G):
    H = F & G
    for h in H:
        N = neighbours(h)
        for n in N:
            if n in H:
                return True
    return False


def voisins():
    global Zones, FZones
    
    Graphe = [[] for _ in range(len(Zones))]
    for i in range(len(Zones)):           
        for j in range(i+1, len(Zones)):
            if sontvoisins(FZones[i], FZones[j]):
                Graphe[i].append(j)
                Graphe[j].append(i)
    return Graphe


def classement():
    ### tri le graphe en construisant une liste : à l'index i, les n° de Zones avec i voisins
    global Graphe

    C = []
    for g in range(len(Graphe)):
        len_g = len(Graphe[g])
        while len_g > len(C) - 1:
            C.append([])
        C[len_g].append(g)
    return C


def recup5(G):
    ### renvoie une zone (tuple) avec au plus 5 voisins
    for g in G:
        if len(G[g]) <= 5:
            return g

def deep_copy_to_tuple(G):
    ### en plus de deep copie trasnforme les élts en tuple (de taille 1) 
    GG = dict()
    for g in range(len(G)):
        GG[(g,)] = [(r,) for r in G[g]]
    return GG

def deep_copy(G):
    GG = dict()
    for g in G:
        GG[g] = G[g][:]
    return GG


def extraire(L, v0, v1):
    ### au moins l'une des 2 valeurs est dans L
    i = 0
    R = []
    while L[i] != v0 and L[i] != v1:
        R.append(L[i])
        i += 1
    i += 1
    while i < len(L) and L[i] != v0 and L[i] != v1:
        R.append(L[i])
        i += 1
    i += 1
    while i < len(L):
        R.append(L[i])
        i += 1
    R.append(v0+v1)
    return R

def reduce(G):
    GG = deep_copy(G)
    g = recup5(GG)
    V = GG[g]
    v0 = V[0]
    # L va contenir les voisins de g et v0
    L = []
    for r in GG[v0]:
        if r != g:
            L.append(r)
    for r in V[1:]:
        if r not in L:
            L.append(r)        
    for v in L:
        GG[v] = extraire(GG[v], g, v0)
    GG[g + v0] = L
    del GG[v0]
    del GG[g]    
    return (GG, v0, g)

def frontiere(G, H):
    global FZones
    Z1 = FZones[G[0]]
    for i in range(1, len(G)):
        Z1 = Z1 | FZones[G[i]]
    Z2 = FZones[H[0]]
    for i in range(1, len(H)):
        Z2 = Z2 | FZones[H[i]]
    return Z1 & Z2


def inv(t):
    ### renvoie la couleur dans sens inverse
    return (t[2], t[1], t[0])

def clignote(Frontiere, coul1, coul2, tps, repet):
    global image
    
    parite = True
    for i in range(2*repet):
        remplir(Frontiere, None, (coul2 if parite else coul1))
        cv2.imshow('Carte', image)
        cv2.waitKey(tps)
        parite = not parite      
    return None


def coloriage6(*args):
    global image, Zones, FZones, Graphe, Couleurs, auto

    G = deep_copy_to_tuple(Graphe)
    tG = (G, 0, 0)                           
    Hist = [tG]
    Front = []
    while len(tG[0]) > 6:
        tG = reduce(tG[0])
        Front.append(frontiere(tG[1], tG[2]))
        if not auto:
            for z in tG[2]:
                remplir(Zones[z], None, (230, 230, 230))
            clignote(Front[-1], (255, 255, 255), (0, 0, 255), 100, 10)
            for z in tG[2]:
                remplir(Zones[z], None, (255, 255, 255))
        remplir(Front[-1], None, (255, 255, 255))
        Hist.append(tG)
        cv2.imshow('Carte', image)
        cv2.waitKey(5)

    c = 0
    C = dict()
    for h in Hist[-1][0]:
        v0, g = Hist[-1][1], Hist[-1][2]
        for z in h:
            C[z] = c
            remplir(Zones[z], None, inv(Couleurs[c]))
        c += 1
    cv2.imshow('Carte', image)
    cv2.waitKey(0)

    H0, v0, g = Hist[-1]    
    i = len(Hist)-2
    while i > -1:
        H, v1, g1 = Hist[i]
        coul = [False]*6
        for x in H[g]:
            for z in x:
                coul[C[z]] = True
        j = 0
        while coul[j]:
            j += 1
        if not auto:
            clignote(Front[i], (255, 255, 255), (0, 0, 255), 100, 10)
        for z in g:
            C[z] = j
            remplir(Zones[z], None, inv(Couleurs[j]))
        remplir(Front[i], None, (0, 0, 0))
        g = g1
        i -= 1
        cv2.imshow('Carte', image)
        cv2.waitKey(5)
    
    return None


def coloriage5(*args):
    global image, Zones, FZones, Graphe, Couleurs, clics, auto

    clics = []
    G = deep_copy_to_tuple(Graphe)
    tG = (G, 0, 0)                           
    Hist = [tG]
    Front = []
    while len(tG[0]) > 5:
        tG = reduce(tG[0])
        Front.append(frontiere(tG[1], tG[2]))
        remplir(Front[-1], None, (255, 255, 255))
        Hist.append(tG)
        cv2.imshow('Carte', image)
        cv2.waitKey(5)

    c = 0
    C = dict()
    for h in Hist[-1][0]:
        v0, g = Hist[-1][1], Hist[-1][2]
        for z in h:
            C[z] = c
            remplir(Zones[z], None, inv(Couleurs[c]))
        c += 1
    cv2.imshow('Carte', image)
    cv2.waitKey(0)

    H0, v0, g = Hist[-1]    
    i = len(Hist)-2
    while i > -1:
        H, v1, g1 = Hist[i]
        coul = [False]*6
        for x in H[g]:
            for z in x:
                coul[C[z]] = True
        j = 0
        while coul[j]:
            j += 1
            
        if j >= 5:
            for z in g:
                remplir(Zones[z], None, (255, 255, 255))
            remplir(Front[i], None, (0, 0, 0))
            
            if not auto:
                recommencer = True
                while recommencer:
                    recup2zones()
                    recommencer, Lzones, coul1, coul2 = select2regions(deep_copy(H), clics[0], clics[1], C)
            else:
                V = H[g]
                v0 = V[0]
                r = 1
                while V[r] in H[v0]:
                    r += 1
                v1 = V[r]
                
                pt0 = Zones[v0[0]].pop()
                Zones[v0[0]].add(pt0)
                pt1 = Zones[v1[0]].pop()
                Zones[v1[0]].add(pt1)
                
                clics = [pt0, pt1]
                recommencer, Lzones, coul1, coul2 = select2regions_auto(deep_copy(H), clics[0], clics[1], C)
                if recommencer:
                    sV = set(V)
                    sV.remove(v0)
                    sV.remove(v1)
                    w0 = sV.pop()
                    for w in H[w0]:
                        if w in sV:
                            sV.remove(w)
                    w1 = sV.pop()
             
                    pt0 = Zones[w0[0]].pop()
                    Zones[w0[0]].add(pt0)
                    pt1 = Zones[w1[0]].pop()
                    Zones[w1[0]].add(pt1)
                    clics = [pt0, pt1]
                    recommencer, Lzones, coul1, coul2 = select2regions_auto(deep_copy(H), clics[0], clics[1], C)

                
            c1 = Couleurs.index(coul1)
            c2 = Couleurs.index(coul2)
            for z in Lzones:
                if C[z] == c1:
                    C[z] = c2
                    remplir(Zones[z], None, inv(Couleurs[c2]))
                else:
                    C[z] = c1
                    remplir(Zones[z], None, inv(Couleurs[c1]))

            if not auto:
                cv2.imshow('Carte', image)
                cv2.waitKey(10)            

            coul = [False]*6
            for x in H[g]:
                for z in x:
                    coul[C[z]] = True
            j = 0
            while coul[j]:
                j += 1
 
        
        for z in g:
            C[z] = j
            remplir(Zones[z], None, inv(Couleurs[j]))
            remplir(Front[i], None, (0, 0, 0))
        g = g1
        i -= 1
        cv2.imshow('Carte', image)
        cv2.waitKey(5)
    return None



def border(n):
    global WIDTH, HEIGHT, image

    In = {(x, y) for x in range(n, WIDTH-n-2) for y in range(n, HEIGHT-n-2)}
    Out = {(x, y) for x in range(WIDTH) for y in range(n)} | {(x, y) for x in range(WIDTH) for y in range(HEIGHT-n-1, HEIGHT)} | {(x, y) for x in range(n) for y in range(n, HEIGHT-n)} | {(x, y) for x in range(WIDTH-n-1, WIDTH) for y in range(n, HEIGHT-n)}
    
    image[0:n, 0:WIDTH] = (0, 0, 0)
    image[HEIGHT-n-1:HEIGHT, 0:WIDTH] = (0, 0, 0)
    image[n:HEIGHT-n, 0:n] = (0, 0, 0)
    image[n:HEIGHT-n, WIDTH-n-1:WIDTH] = (0, 0, 0)
    return In, Out


def neighbourhood():
    global image, Graphe, Zones
    
    for i in range(len(Graphe)):
        color(Zones[i], len(Graphe[i]), (0, 0, 0))
        #color(Zones[i], i, (0, 0, 0))
       
    cv2.imshow('Carte', image)
    cv2.waitKey(0)
    return None

def front_ext(L):
    global FZones
    F = FZones[L[0]]
    for z in L[1:]:
        F = F ^ FZones[z]
    return F


def select2regions(G, pt1, pt2, C):
    global Zones, FZones, image, Couleurs

    (b1, g1, r1) = image[pt1[1], pt1[0]]
    coul1 = (r1, g1, b1)
    (b2, g2, r2) = image[pt2[1], pt2[0]]
    coul2 = (r2, g2, b2)
    
    i = 0
    while pt1 not in Zones[i]:
        i += 1
    j = 0
    L = list(G.keys())
    while i not in L[j]:
        j += 1
    zone0 = set()
    zone = set()
    zone.add(L[j])

    while len(zone0) != len(zone):
        zone0 = zone
        zone = set()
        for z in zone0:
            zone.add(z)
            print(z, G[z])
            for z2 in G[z]:
                x, y = Zones[z2[0]].pop()
                Zones[z2[0]].add((x, y))
                (b, g, r) = image[y, x]
                if (r, g, b) == coul1 or (r, g ,b) == coul2:
                    zone.add(z2)
    Lzones = []
    for z in zone:
        for z2 in z:
            Lzones.append(z2)

    for r in range(40):
        for z in Lzones:
            if r%2 == 0:
                remplir(Zones[z], None, (211, 211, 211))
            else:
                remplir(Zones[z], None, inv(Couleurs[C[z]]))
        cv2.imshow('Carte', image)
        cv2.waitKey(20)

    i = 0
    while pt2 not in Zones[i]:
        i += 1
        
    if i in Lzones:
        print('Problème : on ne peut pas échanger les 2 couleurs.')
        return True, Lzones, coul1, coul2
    else:
        print('On peut echanger les 2 couleurs.')
        return False, Lzones, coul1, coul2
        
    
def select2regions_auto(G, pt1, pt2, C):
    global Zones, FZones, image, Couleurs

    (b1, g1, r1) = image[pt1[1], pt1[0]]
    coul1 = (r1, g1, b1)
    (b2, g2, r2) = image[pt2[1], pt2[0]]
    coul2 = (r2, g2, b2)


    i = 0
    while pt1 not in Zones[i]:
        i += 1
    j = 0
    L = list(G.keys())
    while i not in L[j]:
        j += 1
    zone0 = set()
    zone = set()
    zone.add(L[j])

    while len(zone0) != len(zone):
        zone0 = zone
        zone = set()
        for z in zone0:
            zone.add(z)
            for z2 in G[z]:
                x, y = Zones[z2[0]].pop()
                Zones[z2[0]].add((x, y))
                (b, g, r) = image[y, x]
                if (r, g, b) == coul1 or (r, g ,b) == coul2:
                    zone.add(z2)
    Lzones = []
    for z in zone:
        for z2 in z:
            Lzones.append(z2)


    i = 0
    while pt2 not in Zones[i]:
        i += 1
        
    if i in Lzones:
        print('Problème : on ne peut pas échanger les 2 couleurs.')
        return True, Lzones, coul1, coul2
    else:
        print('On peut echanger les 2 couleurs.')
        return False, Lzones, coul1, coul2
        



def onMouse(event, x, y, flags, param):
    global clics, image

    if event == cv2.EVENT_LBUTTONDOWN:
       print('x = %d, y = %d de couleur %s'%(x, y, str(image[y, x])))
       if len(clics) == 2:
           clics[1] = (x, y)
       else:
           clics.append((x,y))


def recup2zones():
    global image, clics
    
    clics = []
    cv2.setMouseCallback('Carte', onMouse)

    while len(clics) < 2 or (len(clics) == 2 and str(image[clics[0][1], clics[0][0]]) == str(image[clics[1][1], clics[1][0]])):
        cv2.imshow('Carte', image)
        cv2.waitKey(5)

    return None




def next_rapide(L0, LS0, Coul0, Max):
    global image, Zones, Graphe, Couleurs, auto
    
    L = L0[1:]
    LS = {e for e in LS0}
    Coul = Coul0[:]
    
    if len(L0) == 0:
        for r in range(len(Zones)):
            remplir(Zones[r], None, inv(Couleurs[Coul[r]]))
        cv2.imshow('Carte', image)
        return True
    r = L0[0]
    V = Graphe[r]
    CoulDispo = [True] * Max
    nb_ajout = 0
    for v in V:
        if Coul[v] != None:
            CoulDispo[Coul[v]] = False
        if v not in LS:
            LS.add(v)
            L.append(v)
            nb_ajout += 1
    for c in range(Max):
        if CoulDispo[c]:
            Coul[r] = c
            if not auto:
                remplir(Zones[r], None, inv(Couleurs[c]))
                cv2.imshow('Carte', image)
                cv2.waitKey(1)            
            valide = next_rapide(L, LS, Coul, Max)
            if not valide:
                Coul[r] = None
                if not auto:
                    remplir(Zones[r], None, (255, 255, 255))
            else:
                return True

    return False


def coloriage_backtrack(*args):
    ### le parametre est contenue dans args[1][0]
    global Zones

    next_rapide([0], {0}, [None]*len(Zones), args[1][0])

    return None


def effacer(*args):
    global image, Zones
    
    for z in Zones:
        remplir(z, None, (255, 255, 255))
    cv2.imshow('Carte', image)
    return None
    

def automatique(*args):
    global auto
    auto = not auto
    return None


# Couleurs : liste de 6 couleurs :
# Out : ensemble de points du cadre (bord de l'image en noir)
# In : ensemble des points dans l'image (en blanc au départ)

# Zones : liste qui à une région d'index i on associe l'ensemble des points de la région
# FZones : liste qui une région d'index i on associe l'ensemble des points de la frontière de la région

# Graphe : liste qui à une région d'index i associe la liste des index de région voisines (listes triées croissantes)



def main():
    global WIDTH, HEIGHT, image, In, Out, Zones, FZones, Graphe, Couleurs, clics, auto

    sys.setrecursionlimit(10**5)
    chemin_donnees = 'Intermediaires/'
    chemin_resultat = 'Resultats/'
    
    auto = False

    try:
        Tk().withdraw()
        file = askopenfilename()
        image = cv2.imread(file)
    except IOError:
        file = 'vide.png'
        image = cv2.imread(file)
    HEIGHT, WIDTH = image.shape[:2]

# Orange, Bleu, Jaune, Violet, Vert, Rouge
    Couleurs = [(250, 162, 76), (98, 178, 234), (242, 212, 0),
                (157, 57, 205), (114, 236, 93), (247, 62, 111)] 

    filename = ''
    i = len(file)-1
    while i > 0 and file[i] != '/':
        filename = file[i] + filename
        i -= 1
    print(filename, file)
    Zones, FZones, Graphe,In, Out = [], [], [], set(), set()
    file_dump = [filename[:-4] + '_Zones.dump', filename[:-4] + '_FZones.dump', filename[:-4] + '_Graphe.dump']
    file_dump = [chemin_donnees + f for f in file_dump]
    if os.path.isfile(file_dump[0]):
        for i in range(len(file_dump)):
            infile = open(file_dump[i],'rb')
            if i == 0:
                Zones = pickle.load(infile)
            elif i == 1:
                FZones = pickle.load(infile)
            elif i == 2:
                Graphe = pickle.load(infile)
            elif i == 3:
                In = pickle.load(infile)  
            else:
                Out = pickle.load(infile)  
            infile.close()
    else:
        In, Out = border(1)
        allareas()
        for i in range(len(file_dump)):
            outfile = open(file_dump[i], 'wb')
            if i == 0:
                pickle.dump(Zones, outfile)
            elif i == 1:
                pickle.dump(FZones, outfile)
            elif i == 2:
                pickle.dump(Graphe, outfile)
            elif i == 3:
                pickle.dump(In, outfile)
            else:
                pickle.dump(Out, outfile)
            outfile.close()
            cv2.imwrite(chemin_donnees + filename[:-4] + '_NB' + filename[-4:], image) 
            

            
    cv2.imshow('Carte', image)


    cv2.createButton("Effacer", effacer, [])
    cv2.createButton("Automatique", automatique, [], 1, 0)
    cv2.createButton("Algorithme d'Euler", coloriage6, [], cv2.QT_NEW_BUTTONBAR)
    cv2.createButton("Algorithme de Kempe", coloriage5, [], cv2.QT_NEW_BUTTONBAR)
    cv2.createButton("Algorithme avec backtracking", coloriage_backtrack, [4], cv2.QT_NEW_BUTTONBAR)

    
    
    cv2.imshow('Carte', image)
    cv2.waitKey(0)
        
    cv2.imwrite(chemin_resultat + filename[:-4] + '_save' + str(int(time.time())) + filename[-4:], image) 

    cv2.destroyAllWindows()

    


if __name__ == '__main__':
    main()  

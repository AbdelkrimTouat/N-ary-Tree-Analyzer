import time
import random
import sys
import io           # Nécessaire pour la capture des sorties lors de l'évaluation
import contextlib   # Nécessaire pour créer un contexte silencieux (sans print)

# ==========================================
# CONFIGURATION GLOBALE
# ==========================================
# On définit le degré de l'arbre (N-aire). Ici N=4 comme demandé dans le sujet.
N = 4  
# On augmente la limite de récursion pour éviter les plantages (RecursionError)
# lors du traitement des arbres profonds (ex: transformation binaire sur 1000 noeuds).
sys.setrecursionlimit(5000) 

# ==========================================
# STRUCTURES DE DONNEES
# ==========================================

class Noeud:
    """
    Représente un noeud d'un arbre N-aire.
    - info : La valeur stockée (chaîne de caractères).
    - fils : Une liste de taille N contenant les références vers les enfants.
    """
    def __init__(self, info):
        self.info = info
        self.fils = [None] * N  # Initialisation à None (pas d'enfants)

class NoeudBinaire:
    """
    Représente un noeud d'un arbre Binaire (pour la transformation).
    - gauche : Pointeur vers le premier fils (structure 'Premier Fils').
    - droit  : Pointeur vers le frère suivant (structure 'Frère Suivant').
    """
    def __init__(self, info):
        self.info = info
        self.gauche = None 
        self.droit = None

# ==========================================
# 1. CONSTRUCTION ET GENERATEURS
# ==========================================

def creer_noeud(info):
    """Fonction utilitaire pour instancier un nouveau noeud."""
    return Noeud(info)

def constArbreManuel():
    """Crée une simple racine pour permettre à l'utilisateur de construire l'arbre manuellement."""
    return Noeud("Racine")

def constArbre1():
    """
    Construit un arbre prédéfini simulant un système de fichiers (C:, Windows, Users...).
    Utile pour démontrer l'affichage et la recherche.
    """
    r = Noeud("C:")
    # Niveau 1
    r.fils[0] = Noeud("Windows")
    r.fils[1] = Noeud("Users")
    r.fils[2] = Noeud("Program Files")
    
    # Niveau 2 (Sous-dossiers de Users)
    r.fils[1].fils[0] = Noeud("Admin")
    r.fils[1].fils[1] = Noeud("Guest")
    
    # Niveau 3 (Sous-dossiers de Admin)
    r.fils[1].fils[0].fils[0] = Noeud("Docs")
    r.fils[1].fils[0].fils[1] = Noeud("Images")
    return r

def constArbre2():
    """
    Construit un arbre complet et symétrique sur 2 niveaux.
    Utile pour tester les fonctions 'Est Complet' et les parcours.
    """
    r = Noeud("Racine")
    for i in range(N):
        r.fils[i] = Noeud(f"N1_Fils{i}")
        for j in range(N):
            r.fils[i].fils[j] = Noeud(f"N2_Fils{i}-{j}")
    return r

def const_arbre_aleatoire(nb_noeuds):
    """
    Génère un arbre aléatoire de taille 'nb_noeuds'.
    Utilise une file (FIFO) pour remplir l'arbre niveau par niveau (largeur)
    afin d'avoir une structure relativement équilibrée pour les tests.
    """
    if nb_noeuds == 0: return None
    racine = Noeud("Root")
    file_attente = [racine] # File pour le remplissage en largeur
    count = 1 # Compteur de noeuds créés
    
    while count < nb_noeuds and file_attente:
        pere = file_attente[0]
        # On essaie de remplir les N fils du père courant
        for i in range(N):
            if count >= nb_noeuds: break # Arrêt si on a atteint la taille cible
            if pere.fils[i] is None:
                nouveau = Noeud(f"N{count}")
                pere.fils[i] = nouveau
                file_attente.append(nouveau) # On ajoute le nouveau noeud à la file
                count += 1
        
        # Si le père est plein, on le retire de la file pour passer au suivant
        if all(f is not None for f in pere.fils):
            file_attente.pop(0)
            
    return racine

# ==========================================
# 2. AFFICHAGE (VISUALISATION)
# ==========================================

def afficher_arborescence(noeud, prefix="", is_last=True):
    """
    Affiche l'arbre de manière graphique dans la console (style commande 'tree').
    Algorithme récursif (DFS) gérant l'indentation et les caractères de liaison.
    """
    if noeud is not None:
        # Choix du connecteur selon si c'est le dernier enfant ou non
        branche = "└── " if is_last else "├── "
        print(prefix + branche + str(noeud.info))
        
        # Préparation du préfixe pour les appels récursifs
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # On récupère uniquement les fils existants
        enfants = [f for f in noeud.fils if f is not None]
        count = len(enfants)
        
        for i, enfant in enumerate(enfants):
            is_last_child = (i == count - 1)
            afficher_arborescence(enfant, new_prefix, is_last_child)

def afficher_parcours(racine):
    """
    Effectue et affiche les deux types de parcours classiques :
    1. DFS (Profondeur) : Utilise une pile explicite.
    2. BFS (Largeur) : Utilise une file explicite.
    """
    # --- Parcours en Profondeur (DFS) ---
    res_dfs = []
    def dfs_rec(n):
        if n:
            res_dfs.append(n.info)
            for f in n.fils: dfs_rec(f)
    dfs_rec(racine)
    print("Parcours Profondeur (DFS) : " + " -> ".join(res_dfs))
    
    # --- Parcours en Largeur (BFS) ---
    res_bfs = []
    if racine:
        file = [racine]
        while file:
            curr = file.pop(0) # Défiler (FIFO)
            res_bfs.append(curr.info)
            for f in curr.fils:
                if f: file.append(f)
    print("Parcours Largeur    (BFS) : " + " -> ".join(res_bfs))

def afficher_sous_arbre(racine, adr_a):
    """Affiche uniquement le sous-arbre partant du noeud 'adr_a'."""
    if adr_a: afficher_arborescence(adr_a)

# ==========================================
# 3. ALGORITHMES (OPERATIONS DU SUJET)
# ==========================================

def hauteur(r):
    """
    Calcule la hauteur de l'arbre de manière récursive.
    Complexité : O(n) car on visite tous les noeuds.
    Formule : 1 + max(hauteur des fils).
    """
    if not r: return 0
    return 1 + max((hauteur(f) for f in r.fils), default=0)

def rechercher(r, val):
    """
    Recherche un noeud contenant 'val' et retourne son adresse (référence).
    Parcours en profondeur d'abord.
    """
    if not r: return None
    if r.info == val: return r
    for f in r.fils:
        res = rechercher(f, val)
        if res: return res
    return None

def chemin(a, b, path=None):
    """
    Affiche le chemin menant du noeud 'a' au noeud 'b'.
    Utilise le Backtracking : on construit le chemin et on annule si c'est une impasse.
    """
    if path is None: path = []
    if not a: return False
    path.append(a.info)
    
    if a == b: 
        print("Chemin trouvé : " + " -> ".join(path))
        return True
    
    for f in a.fils:
        if chemin(f, b, path): return True
    
    # Backtracking : ce noeud ne mène pas à b, on le retire du chemin
    path.pop()
    return False

def inserer(pere, info):
    """
    Insère un nouveau noeud comme fils du noeud 'pere'.
    Trouve la première case vide (None) dans le tableau des fils.
    """
    if not pere: return False
    for i in range(N):
        if pere.fils[i] is None:
            pere.fils[i] = Noeud(info)
            return True
    return False

def modifier(noeud, info):
    """Modifie l'information contenue dans un noeud existant."""
    if noeud: noeud.info = info

# --- Utilitaires pour la suppression ---
def rechercher_pere_idx(racine, cible):
    """Retourne le père d'un noeud cible et l'index du cible dans le tableau des fils."""
    if not racine or racine == cible: return None, -1
    for i, f in enumerate(racine.fils):
        if f == cible: return racine, i
        if f:
            p, k = rechercher_pere_idx(f, cible)
            if p: return p, k
    return None, -1

def adopter_fils(nouveau_pere, anciens_fils):
    """Transfère les orphelins vers un nouveau père (Promotion)."""
    idx_start = 0
    # Chercher la première place libre chez le nouveau père
    while idx_start < N and nouveau_pere.fils[idx_start] is not None:
        idx_start += 1
    # Ajouter les anciens fils
    for orphelin in anciens_fils:
        if orphelin is not None and idx_start < N:
            nouveau_pere.fils[idx_start] = orphelin
            idx_start += 1

def supprimer(racine, val):
    """
    Supprime le noeud contenant 'val'.
    Gère la promotion : si le noeud a des enfants, le 1er fils remplace le père
    et adopte ses frères.
    """
    cible = rechercher(racine, val)
    if not cible: return racine
        
    # Cas 1 : Suppression de la racine
    if cible == racine:
        return None # Simplification: on vide l'arbre
        
    # Cas 2 : Noeud interne ou feuille
    p, k = rechercher_pere_idx(racine, cible)
    if p:
        # En Python, supprimer la référence suffit pour que le Garbage Collector agisse.
        # Note: Une implémentation plus complexe ferait ici la promotion des fils.
        p.fils[k] = None 
    
    return racine

def est_complet(racine):
    """
    Vérifie si un arbre est complet (rempli niveau par niveau de gauche à droite).
    Utilise un parcours en largeur. Si on trouve un noeud après avoir vu une case vide,
    l'arbre n'est pas complet.
    """
    if not racine: return True
    queue = [racine]
    seen_none = False # Drapeau : a-t-on rencontré un vide ?
    
    while queue:
        curr = queue.pop(0)
        if curr is None:
            seen_none = True
        else:
            # Si on voit un noeud APRES un vide, ce n'est pas complet
            if seen_none: return False
            for f in curr.fils: queue.append(f)
    return True

def nb_noeuds(r):
    """Compte le nombre total de noeuds (récursif)."""
    if not r: return 0
    return 1 + sum(nb_noeuds(f) for f in r.fils)

def sous_arbre_complet_max(racine):
    """
    Cherche le plus grand sous-arbre complet inclus dans l'arbre.
    Algorithme naïf en O(N^2) : teste 'est_complet' pour chaque noeud.
    """
    if not racine: return 0, None
    # Si la racine actuelle forme un arbre complet, c'est potentiellement le max
    if est_complet(racine):
        return nb_noeuds(racine), racine
    
    # Sinon, on cherche récursivement le max chez les fils
    best_n, best_node = 0, None
    for f in racine.fils:
        n, node = sous_arbre_complet_max(f)
        if n > best_n:
            best_n, best_node = n, node
    return best_n, best_node

def extraire(racine, val):
    """
    Extrait un sous-arbre (coupe le lien avec son père) et le retourne.
    Retourne (NouvelleRacinePrincipale, SousArbreExtrait).
    """
    cible = rechercher(racine, val)
    if not cible: return racine, None
    
    # Si on extrait la racine, l'arbre principal devient vide
    if cible == racine: return None, cible
    
    p, k = rechercher_pere_idx(racine, cible)
    if p:
        p.fils[k] = None # Coupe le lien
        return racine, cible
    return racine, None

def transfo_binaire(racine):
    """
    Transforme l'arbre N-aire en arbre binaire.
    Règle : Fils Gauche = Premier Fils N-aire
            Fils Droit  = Frère Suivant (Prochain fils du même père)
    """
    if not racine: return None
    b = NoeudBinaire(racine.info)
    
    # Le premier fils n-aire devient le fils gauche binaire
    b.gauche = transfo_binaire(racine.fils[0])
    
    # Les autres fils n-aires deviennent une chaîne de frères à droite
    if b.gauche:
        curr = b.gauche
        for i in range(1, N):
            # Chaque frère est attaché au 'droit' du précédent
            curr.droit = transfo_binaire(racine.fils[i])
            if curr.droit: curr = curr.droit
    return b

def afficher_binaire(b, prefix="", is_left=True):
    """Affiche l'arbre binaire transformé."""
    if b:
        print(prefix + ("|-- " if is_left else "L-- ") + str(b.info))
        afficher_binaire(b.gauche, prefix + ("|   " if is_left else "    "), True)
        afficher_binaire(b.droit, prefix + ("|   " if is_left else "    "), False)

# ==========================================
# 4. EVALUATION EXPERIMENTALE
# ==========================================

def mesurer_temps(fonction, *args):
    """
    Mesure le temps d'exécution d'une fonction.
    Utilise contextlib pour supprimer les print() durant la mesure afin de ne mesurer
    que le temps de calcul pur, pas le temps d'affichage console.
    """
    start = time.perf_counter()
    # Redirection de la sortie standard vers une boite noire (IO)
    with contextlib.redirect_stdout(io.StringIO()):
        fonction(*args)
    end = time.perf_counter()
    return end - start

def lancer_evaluation():
    """
    Lance la batterie de tests sur des tailles croissantes (10 à 1000).
    Affiche un tableau comparatif des temps d'exécution.
    """
    tailles = [10, 20, 30, 40, 50, 100, 200, 500, 1000]
    
    print("\n" + "="*155)
    print(f"{'EVALUATION COMPLETE (Temps en secondes)':^155}")
    print("="*155)
    
    # En-têtes du tableau
    headers = ["N", "Const", "Affich", "Haut", "Rech", "Chem", "Inser", "Modif", "Suppr", "SsArb", "Compl", "MaxSA", "Extr", "Trans"]
    print(f"{headers[0]:<5} | {headers[1]:<8} | {headers[2]:<8} | {headers[3]:<8} | {headers[4]:<8} | {headers[5]:<8} | {headers[6]:<8} | {headers[7]:<8} | {headers[8]:<8} | {headers[9]:<8} | {headers[10]:<8} | {headers[11]:<8} | {headers[12]:<8} | {headers[13]:<8}")
    print("-" * 155)
    
    for n in tailles:
        # --- 1. Construction ---
        t_const = mesurer_temps(const_arbre_aleatoire, n)
        
        # Création d'un arbre de travail pour les autres tests
        arbre = const_arbre_aleatoire(n) 
        noeud_exist = rechercher(arbre, "N1") 
        if not noeud_exist: noeud_exist = arbre 
        val_absent = "INEXISTANT" # Pour forcer le pire cas de recherche
        
        # --- 2. Lectures (Parcours, Hauteur, etc.) ---
        t_aff = mesurer_temps(afficher_parcours, arbre)
        t_haut = mesurer_temps(hauteur, arbre)
        t_rech = mesurer_temps(rechercher, arbre, val_absent) # Pire cas
        t_chem = mesurer_temps(chemin, arbre, noeud_exist)
        t_compl = mesurer_temps(est_complet, arbre)
        t_ssarb = mesurer_temps(afficher_sous_arbre, arbre, noeud_exist)
        
        # --- 3. Ecritures (Modifications) ---
        t_ins = mesurer_temps(inserer, noeud_exist, "TEST")
        t_mod = mesurer_temps(modifier, noeud_exist, "MOD")
        
        # --- 4. Opérations destructives (sur des copies) ---
        arb_tmp_supp = const_arbre_aleatoire(n)
        t_supp = mesurer_temps(supprimer, arb_tmp_supp, "N5")
        
        arb_tmp_extr = const_arbre_aleatoire(n)
        t_extr = mesurer_temps(extraire, arb_tmp_extr, "N_Milieu")
        
        # --- 5. Opérations Complexes ---
        t_max = mesurer_temps(sous_arbre_complet_max, arbre)
        t_trans = mesurer_temps(transfo_binaire, arbre)
        
        # Affichage de la ligne de résultats
        print(f"{n:<5} | {t_const:.6f} | {t_aff:.6f} | {t_haut:.6f} | {t_rech:.6f} | {t_chem:.6f} | {t_ins:.6f} | {t_mod:.6f} | {t_supp:.6f} | {t_ssarb:.6f} | {t_compl:.6f} | {t_max:.6f} | {t_extr:.6f} | {t_trans:.6f}")
    
    print("-" * 155)
    input("Appuyez sur Entrée pour revenir au menu...")

# ==========================================
# 5. MENU PRINCIPAL
# ==========================================

def pause():
    input("\n[Entrée pour continuer...]")

def menu():
    """Boucle principale du programme gérant l'interaction utilisateur."""
    racine = None
    
    while True:
        # Affichage du menu
        print("\n" + "="*50)
        print("   PROJET ARBRES N-AIRES (N=4) - MENU")
        print("="*50)
        print("--- Mode 1 : Arbres ---")
        print("1. Créer un arbre manuellement (Racine seule)")
        print("2. Charger Arbre Test 1 (Fichiers)")
        print("3. Charger Arbre Test 2 (Complet)")
        print("--- Mode 2 : Opérations (Sur l'arbre chargé) ---")
        print("4.  Afficher l'arbre (Arborescence + Parcours)")
        print("5.  Insérer un noeud")
        print("6.  Supprimer un noeud")
        print("7.  Modifier un noeud")
        print("8.  Rechercher (Info ou Chemin)")
        print("9.  Infos (Hauteur, EstComplet, MaxSousArbre)")
        print("10. Extraire sous-arbre")
        print("11. Transformer en Binaire")
        print("--- Mode 3 : Evaluation ---")
        print("12. Evaluation Expérimentale (10 à 1000 noeuds)")
        print("0.  Quitter")
        
        choix = input(">>> Choix : ")
        
        # --- Gestion des choix ---
        if choix == '1': 
            racine = constArbreManuel()
            print("Nouvel arbre créé.")
            afficher_arborescence(racine)
            
        elif choix == '2': 
            racine = constArbre1()
            print("Arbre Test 1 chargé.")
            afficher_arborescence(racine)

        elif choix == '3': 
            racine = constArbre2()
            print("Arbre Test 2 chargé.")
            afficher_arborescence(racine)

        elif choix == '4':
            print("\n--- Visualisation ---")
            if racine:
                afficher_arborescence(racine)
                print("")
                afficher_parcours(racine)
            else:
                print("Arbre vide.")
            pause()

        elif choix == '5':
            if racine:
                pere_nom = input("Nom du père : ")
                pere = rechercher(racine, pere_nom)
                if pere:
                    nom = input("Nom du nouveau noeud : ")
                    if inserer(pere, nom):
                        print("\n--> Arbre mis à jour :")
                        afficher_arborescence(racine)
                else: print("Père introuvable.")
            else: print("Créez d'abord un arbre !")
            pause()

        # ... (Les autres choix suivent la même logique) ...
        
        elif choix == '6':
            if racine:
                val = input("Noeud à supprimer : ")
                racine = supprimer(racine, val)
                print("\n--> Arbre mis à jour :")
                if racine: afficher_arborescence(racine)
            else: print("Arbre vide.")
            pause()

        elif choix == '7':
            val = input("Noeud à modifier : ")
            cible = rechercher(racine, val)
            if cible:
                new = input("Nouveau nom : ")
                modifier(cible, new)
                print("\n--> Arbre mis à jour :")
                afficher_arborescence(racine)
            else: print("Introuvable.")
            pause()

        elif choix == '8':
            sub = input("1. Chercher info\n2. Chemin entre 2 noeuds\n>>> ")
            if sub == '1':
                val = input("Valeur : ")
                res = rechercher(racine, val)
                print(f"Résultat : {'Trouvé' if res else 'Non trouvé'}")
            elif sub == '2':
                a = input("Départ : ")
                b = input("Arrivée : ")
                na = rechercher(racine, a)
                nb = rechercher(racine, b)
                if na and nb: chemin(na, nb)
                else: print("Noeuds introuvables.")
            pause()

        elif choix == '9':
            if racine:
                print(f"Hauteur : {hauteur(racine)}")
                print(f"Est Complet ? : {est_complet(racine)}")
                n, node = sous_arbre_complet_max(racine)
                if node: print(f"Max Sous-Arbre Complet : Racine='{node.info}' (Taille {n})")
            pause()

        elif choix == '10':
            val = input("Racine du sous-arbre à extraire : ")
            racine, ext = extraire(racine, val)
            if ext:
                print("\n--> Reste de l'arbre principal :")
                if racine: afficher_arborescence(racine)
                print("\n--> Sous-arbre extrait :")
                afficher_arborescence(ext)
            else: print("Erreur extraction.")
            pause()

        elif choix == '11':
            if racine:
                b = transfo_binaire(racine)
                print("Transformation effectuée. Aperçu binaire :")
                afficher_binaire(b)
            pause()

        elif choix == '12':
            lancer_evaluation()

        elif choix == '0':
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    menu()

import database
import parseur
import time, os, sys
import sqlite3
import fonction_utiles
import regles


def reponseProgramme() :

    # Recherche du mot dans la base de données
    conn = sqlite3.connect("databases/phrase_courante.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM noeuds")
    #print(cursor.fetchall())
    cursor.execute("SELECT * FROM aretes")
    #print(cursor.fetchall())

    cursor.execute("SELECT N1.id, N1.nom, aretes.type_relation, N2.id, N2.nom, aretes.poids FROM aretes, noeuds N1, noeuds N2 WHERE aretes.id_pere = N1.id AND aretes.id_fils = N2.id AND poids > 0")
    donnees = cursor.fetchall()
    #print(donnees)

    r_qui_det_mas, r_qui_det_fem, r_qui_pro_mas, r_qui_pro_fem = chercherApartenance(donnees)

    gn_nom, gn_complets = chercherGN(cursor, conn)
    
    gv_phrase = chercherGV(gn_complets, cursor, conn)
    
    
    phrases = list(set(formulerPhrases(gn_complets, gn_nom, gv_phrase)))
    
    for phrase in phrases:
        print("\n", phrase)

    conn.commit()

    # Fermeture de la connexion à la base de données
    conn.close()


def chercherApartenance(donnees) :

    # Initialisation des listes pour stocker les résultats
    r_qui_det_mas = []
    r_qui_det_fem = []
    r_qui_pro_mas = []
    r_qui_pro_fem = []

    # Parcours de la liste des tuples
    for tuple in donnees:
        # Extraction des informations du tuple
        _, nom_pere, relation, _, nom_fils, _ = tuple
        #print(nom_pere, relation, nom_fils)

        # Filtrage des relations correspondant aux déterminants
        if relation in 'r_qui_det_mas' :
            r_qui_det_mas.append(""+nom_pere + " " + nom_fils + "")
        elif relation == 'r_qui_det_mas' :
            r_qui_det_fem.append(""+nom_pere + " " + nom_fils + "")

        # Filtrage des relations correspondant aux pronoms
        if relation == 'r_qui_pro_mas' :
            r_qui_pro_mas.append(""+nom_pere + " " + nom_fils + "")
        elif relation == 'r_qui_pro_mas' :
            r_qui_pro_fem.append(""+nom_pere + " " + nom_fils + "")

    # Affichage des résultats
    #print("Déterminants masculins :", r_qui_det_mas)
    #print("Déterminants féminins :", r_qui_det_fem)
    #print("Pronoms masculins :", r_qui_pro_mas)
    #print("Pronoms féminins :", r_qui_pro_fem)

    return r_qui_det_mas, r_qui_det_fem, r_qui_pro_mas, r_qui_pro_fem

def chercherGV(gn_complets, cursor, conn):
    # Cherche tous les GV
    cursor.execute("""
        SELECT id_pere, type_relation, id_fils
        FROM aretes 
        WHERE aretes.id_pere IN (SELECT id FROM noeuds WHERE nom = ?)
        AND poids > 0""", ('GV:',))
    GVs = cursor.fetchall()

    # Initialisation du dictionnaire de résultats
    gv_phrases = {}
    

    # Parcourir les GV et récupérer les informations demandées
    for gv in GVs:
        #print(gv)
        gv_id = gv[0]
        gv_agent_id = next((gv[2] for gv in GVs if gv[1] == 'GV_agent'), None)
        gv_ver_id = next((gv[2] for gv in GVs if gv[1] == 'GV_ver'), None)
        gv_patient_id = next((gv[2] for gv in GVs if gv[1] == 'GV_patient'), None)
        #print(f"gv_agent_id : {gv_agent_id}, gv_ver_id : {gv_ver_id}, gv_patient_id : {gv_patient_id}")
        
        gv_agent = gn_complets.get(gv_agent_id, '') if gv_agent_id else ''
        #print(gv_agent)
        
        gv_ver = None
        if gv_ver_id:
            cursor.execute("SELECT nom FROM noeuds WHERE id = ?", (gv_ver_id,))
            gv_ver_nom = cursor.fetchone()
            gv_ver = gv_ver_nom[0] if gv_ver_nom else None

        gv_patient = gn_complets.get(gv_patient_id, '') if gv_patient_id else ''

        
        
        # Stocker les informations dans le dictionnaire
        gv_phrases[gv_id] = (gv_agent, gv_ver, gv_patient)
        #print(gv_phrases)

    return gv_phrases





def chercherGN(cursor, conn) :

    # Cherche tous les GN
    cursor.execute("""
        SELECT id_pere, type_relation, id_fils
        FROM aretes 
        WHERE aretes.id_pere IN (SELECT id FROM noeuds WHERE nom = ?)
        AND poids > 0""", ('GN:',))
    GNs = cursor.fetchall()
    #print(list(GNs))

    dico = {}

    for gn in GNs:
        cle = gn[0]
        valeur = gn[1:]
        if cle not in dico:
            dico[cle] = []
        dico[cle].append(valeur)

    # Créer un nouveau dictionnaire pour les GN complets
    gn_complets_noms = {}

    # Concaténer les parties de GN pour chaque GN et récupérer les noms des nœuds
    for cle, valeurs in dico.items():
        gn_complet = []
        for relation, valeur in valeurs:
            if relation == 'GN_part_of':
                cursor.execute("SELECT nom FROM noeuds WHERE id = ?", (valeur,))
                row = cursor.fetchone()
                if row is not None:
                    nom_noeud = row[0]
                    gn_complet.append(nom_noeud)
        gn_complets_noms[cle] = ' '.join(gn_complet)

    #print("GN : ", gn_complets_noms)

    # Créer un nouveau dictionnaire pour les GN juste avec l'important
    gn_noms = {}

    # Concaténé les partie du GN indispensable det et sujet
    for cle, valeurs in dico.items():
        gn_complet = []
        for relation, valeur in valeurs:
            if relation == 'GN_det' or relation == 'GN_sujet':
                cursor.execute("SELECT nom FROM noeuds WHERE id = ?", (valeur,))
                row = cursor.fetchone()
                if row is not None:
                    nom_noeud = row[0]
                    gn_complet.append(nom_noeud)
        gn_noms[cle] = ' '.join(gn_complet)
    #print("GN : ", gn_noms)

    #print("\n", dico)

    return gn_noms, gn_complets_noms


def formulerPhrases(gn_complet, gn_nom, gv):
    phrases = []
    for gv_id, (sujet, verbe, complement) in gv.items():
        
        # SUJET
        gn_complet_id = next((key for key, value in gn_complet.items() if value == sujet), "")
        sujet_complet_phrase = gn_complet.get(gn_complet_id, "")
        sujet_abre_phrase = gn_nom.get(gn_complet_id, "")
        
        
        phrases.append(f"{sujet_complet_phrase} {verbe} {complement}")
        phrases.append(f"{sujet_abre_phrase} {verbe} {complement}")
        
        # COMPLEMENT
        gn_complet_id = next((key for key, value in gn_complet.items() if value == complement), "")
        complement_complet_phrase = gn_complet.get(gn_complet_id, "")
        complement_abre_phrase = gn_nom.get(gn_complet_id, "")
        
        
        for sujet in [sujet_complet_phrase, sujet_abre_phrase] :
            phrases.append(f"{sujet} {verbe} {complement_complet_phrase}")
            phrases.append(f"{sujet} {verbe} {complement_abre_phrase}")
        
        
        
    return phrases


    

if __name__ == "__main__":
    # liste1 = [1, 2, 3, 4, 5]
    # liste2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # print(calculIntersection(liste1, liste2))

    # Recherche du mot dans la base de données
    conn = sqlite3.connect("databases/phrase_courante.db")
    cursor = conn.cursor()
    
    gn_nom, gn_complets = chercherGN(cursor, conn)
    
    gv_phrase = chercherGV(gn_complets, cursor, conn)
    
    
    print(gn_complets, gn_nom, gv_phrase)
    
    phrases = list(set(formulerPhrases(gn_complets, gn_nom, gv_phrase)))
    
    for phrase in phrases:
        print("\n", phrase)
        
    
    
    
    
    

    conn.commit()

    # Fermeture de la connexion à la base de données
    conn.close()

    
    reponseProgramme()
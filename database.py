import sqlite3
import time
import parseur
import fonction_utiles
import networkx as nx
import matplotlib.pyplot as plt




def search_name_in_noeuds(dict_noeuds, nom, is_debut=0, is_fin=0, filtre={}, verbose=0):
    noeuds = []
    for id, noeud in dict_noeuds.items():
        if (noeud["nom"] == nom) and (noeud["is_debut"]
                                      == is_debut) and (noeud["is_fin"]
                                                        == is_fin):
            noeud["id"] = id
            noeuds.append(noeud)

    if filtre != {}:
        for noeud in noeuds:
            if noeud["nom"] in filtre.keys():
                return noeud

    return noeuds[0] if noeuds != [] else None


def create_database(verbose=0):

    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()
    print("Création de la database réussie")

    # Reseau dump
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reseau_dump (
        id INTEGER PRIMARY KEY,
        eid INTEGER,
        terme TEXT,
        definition TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS node_types (
        id INTEGER PRIMARY KEY,
        ntid INTEGER,
        ntname TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY,
        eid INTEGER,
        name TEXT,
        type TEXT,
        w INTEGER,
        formated_name TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS relation_types (
        id INTEGER PRIMARY KEY,
        rtid INTEGER, 
        trname TEXT,
        trgpname TEXT,
        rthelp TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS relations_sortantes (
        id INTEGER PRIMARY KEY,
        rid INTEGER,
        node1 INTEGER,
        node2 INTEGER,
        type TEXT,
        w INTEGER,
        w_normed REAL,
        rank INTEGER
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS relations_entrantes (
        id INTEGER PRIMARY KEY,
        rid INTEGER,
        node1 INTEGER,
        node2 INTEGER,
        type TEXT,
        w INTEGER
    )""")

    # Mots composés
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mots_composes (
        id INTEGER PRIMARY KEY,
        terme TEXT
    )""")

    conn.commit()
    conn.close()

    print("Création de la base dump.db réussie")

    # Tables pour les noeuds
    for table in ["phrase_courante", "phrase_historique"]:
        conn = sqlite3.connect(f"databases/{table}.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS noeuds (
            id INTEGER PRIMARY KEY,
            nom TEXT,
            is_mot INTEGER DEFAULT 0,
            is_debut INTEGER DEFAULT 0,
            is_fin INTEGER DEFAULT 0
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS aretes (
            id_pere INTEGER,
            id_fils INTEGER,
            type_relation TEXT,
            poids INTEGER DEFAULT 100,
            PRIMARY KEY (id_pere, id_fils, type_relation)
        )""")

        conn.commit()
        conn.close()

    print("Création des tables réussie")





def affichage_tables(tables, base='phrase_courante', close=False):
    
    conn = sqlite3.connect(f"databases/{base}.db")
    cursor = conn.cursor()

    for table in tables:
        # Afficher le contenu des table après les insertions
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        print(f"\n--- Contenu de la table {table} après les insertions:")
        for row in rows:
            print(row)

    if close:
        conn.close()






def insert_mots_composes(verbose=0):

    # Exemple de ligne :
    # 21;"Marcel Gotlieb Gotlib";
    # 23;"art et architecture catalans";

    print("Lecture du fichier mots-composés.txt")
    with open("txt/mots-composés.txt", 'r', encoding='utf-8') as f:
        mots_composes_raw = f.read().splitlines()

    nbMotsInitial = len(mots_composes_raw)

    mots_composes_raw = [
        mot for mot in mots_composes_raw
        if (mot.strip() != '') and not (mot.strip().startswith("//")) and (
            '&' not in mot) and (mot.count('"') == 2) and (
                len(mot.split(';')[1].split(' ')) < 10)
    ]  # opti à l'arache

    print(
        f"nombre de mots composés après tri : {'{:,}'.format(len(mots_composes_raw))}/{'{:,}'.format(nbMotsInitial)}"
    )

    print("Création de noeuds pour les mots composés")
    start_time = time.time()

    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()


    for nb_mot, mots in enumerate(mots_composes_raw):

        if len(mots.strip().split(';')) == 3:
            idPhrase, termes, formated_name = mots.strip().split(';')
            liste_termes = termes.strip('" ').split(' ')

            # insertion dans la table mot composés
            cursor.execute(
                """
            INSERT INTO mots_composes (id, terme)
            VALUES (?, ?)
            """, (idPhrase, termes))

    print("Ajout des noeuds des mots composés en base de données")

    conn.commit()
    conn.close()

    print("Ajout des mots composés réussi")


def insertionPhrase(liste_termes, verbose=0):

    # cherche sur jeu de mot l'id du mot
    # ou alooooors, calculer la taille de la phrase, ça c'est l'id 1, l'id 2, sauf que ça changera rien car si on rajoute un noeud on fais juste +1

    for i, terme in enumerate(liste_termes):

        #idMot = str(i)

        if i == 0:  # premier mot
            # On recherche d'abord si le mot existe déjà dans les noeuds
            cursor.execute(
                "SELECT * FROM noeuds WHERE nom = ? AND is_debut = 1",
                (terme, ))
            noeud_mot = cursor.fetchone()

            if noeud_mot is None:
                cursor.execute(
                    """
                INSERT INTO noeuds (nom, is_debut, is_fin)
                VALUES (?, ?, ?)
                """, (terme, 1, 0))
                ancienIdTerme = cursor.lastrowid
            else:
                ancienIdTerme = noeud_mot[0]

        elif i == len(liste_termes) - 1:  # dernier mot
            cursor.execute(
                """
            INSERT INTO noeuds (id, nom, is_debut, is_fin)
            VALUES (?, ?, ?, ?)
            """, (idMot, terme, 0, 1))
            cursor.execute(
                """
            INSERT INTO aretes(id_pere, id_fils, type_relation)
            VALUES (?, ?, ?)
            """, (ancienIdTerme, idMot, "r_succ"))

        else:
            # on cherche s'il existe déjà un noeud avec ce nom et qui est un fils du noeud précédent (aretes avec ancienIdTerme)
            cursor.execute(
                """
                           SELECT *
                           FROM noeuds
                           JOIN aretes ON noeuds.id = aretes.id_fils
                           WHERE nom = ?
                           AND id_pere = ?
                           AND is_debut = 0
                           AND poid > 0
                           """, (
                    terme,
                    ancienIdTerme,
                ))
            noeud_mot = cursor.fetchone()
            if noeud_mot is None:
                cursor.execute(
                    """
                INSERT INTO noeuds (id, nom, is_debut, is_fin)
                VALUES (?, ?, ?, ?)
                """, (idMot, terme, 0, 0))
                cursor.execute(
                    """
                INSERT INTO aretes (id_pere, id_fils, type_relation)
                VALUES (?, ?, ?)
                """, (ancienIdTerme, idMot, "r_succ"))
                ancienIdTerme = idMot
            else:
                ancienIdTerme = noeud_mot[0]

    return True


def insertionRelationsDump(id_relation, tab_phrase, tab_id_phrase, verbose=0):

    if verbose :
        print(tab_phrase)
        print(tab_id_phrase)
        
    for index, tab in enumerate(tab_phrase):
        tab = tab.lower()
        # mettre en minuscule
        parseur.insertionDumpBDD(tab, verbose=verbose)
        #affichage_tables(["entries", "relations_sortantes"], 'dump',  close=True)


        mot_trouve = []
        temps = 0
        #print(mot_trouve)
        mot_trouve, temps, nom_relation = rechercheDumpBDDComplet(
            tab, id_relation, verbose=verbose)
        

        # Affichage de la définition
        if verbose:
            fonction_utiles.affichageReseauDump(mot_trouve, tab, temps,
                                                nom_relation, id_relation)

        
        conn = sqlite3.connect("databases/phrase_courante.db")
        cursor = conn.cursor()

        for mot in mot_trouve:
            # print(mot)
            # Insertion du noeud simple si c'est pas le même que le base
            if (tab != mot[3].replace("'", "")):
                cursor.execute(
                    """
                    INSERT INTO noeuds(nom) VALUES(?)
                    """, (mot[3].replace("'", ""), ))

                # Derniere insertion (ici le noeuds)
                #print("LastRowid mot : ", cursor.lastrowid)
                id_courant = cursor.lastrowid

                # Le père étant l'index du tab courant
                if verbose :
                    print("Tab : 1 ", tab_phrase)
                id_pere = tab_id_phrase[index]
                if verbose :
                    print("Id_pere : ", id_pere)

                # Insertion de l'arrete associé
                cursor.execute(
                    """
                    INSERT INTO aretes(id_pere, id_fils, type_relation) VALUES(?,?,?)
                    """, (
                        id_pere,
                        id_courant,
                        nom_relation[1].replace("'", ""),
                    ))

        if verbose:
            affichage_tables(["noeuds", "aretes"])

        conn.commit()
        conn.close()



# Fonction qui insert dans la bdd graphe la phrase actuel
def insertPhraseToBDD(tab_phrase, database="phrase_courante", verbose=0):

    tab_phrase = ["_START"] + tab_phrase + ["_END"]
    tab_id_phrase = []

    conn = sqlite3.connect(f"databases/{database}.db")
    cursor = conn.cursor()

    id_precedent = -1
    for tab in tab_phrase:

        # Insertion du noeud simple
        cursor.execute(
            """
            INSERT INTO noeuds(nom, is_mot) 
            VALUES(?, 1)
            """, (tab, ))

        #print("Lastrowid : ", cursor.lastrowid)
        id_courant = cursor.lastrowid
        tab_id_phrase.append(id_courant)

        if id_precedent != -1:
            # Insertion de l'arrete associé
            cursor.execute(
                """
                INSERT INTO aretes(id_pere, id_fils, type_relation) 
                VALUES(?, ?, ?)
                """, (
                    id_precedent,
                    id_courant,
                    "r_succ",
                ))

        id_precedent = id_courant

    if verbose :
        affichage_tables(['aretes', 'noeuds'])

    # N'oubliez pas de commit les changements
    conn.commit()
    if verbose:
        print("\n\n---- DECONNEXION BDD ----\n")
    conn.close()

    return tab_id_phrase


def supressionLigne(liste_table, base, verbose=0):
    # On vide les tables
    conn = sqlite3.connect(f"databases/{base}.db")
    cursor = conn.cursor()
    # Boucle pour supprimer toutes les lignes de chaque table
    for table in liste_table:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except:
            pass
    print("Suppression des lignes terminés")
    conn.commit()
    if verbose:
        print("\n\n---- DECONNEXION BDD ----\n")
    conn.close()


def rechercheMotComposeBDD(mot_compose, verbose=0):

    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()


    if verbose:
        print("\n\n---- RECHERCHE DEBUT ----")
    print(f"\nRecherche du mot '{mot_compose}' : \n")
    temps_mot = time.time()

    # Utilisez un tuple pour les paramètres de substitution
    cursor.execute("SELECT id, terme FROM mots_composes WHERE terme = ?",
                   (mot_compose, ))
    phrase_bdd_complet = cursor.fetchone()

    # Utilisez un tuple pour les paramètres de substitution (" %" car mot entier pas de changement de verbe)
    cursor.execute(
        "SELECT id, terme FROM mots_composes WHERE terme LIKE ? AND terme <> ?",
        (mot_compose + " %", mot_compose))
    phrase_bdd_tous = cursor.fetchall()
    # phrase_bdd_tous = None

    temps = time.time() - temps_mot


    if verbose:
        print("\n---- RECHERCHE FINI ----")

    # Fonction qui met à jour
    conn.commit()

    # Fermeture de la connexion à la base de données
    if verbose:
        print("\n\n---- DECONNEXION BDD ----\n")
    conn.close()

    return phrase_bdd_complet, phrase_bdd_tous, temps



def rechercheDumpBDD(mot, verbose=0):

    # Recherche du mot dans la base de données
    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()

    timeStart = time.time()

    cursor.execute(
        "SELECT id, eid, terme, definition FROM reseau_dump WHERE terme = ? ",
        (mot, ))
    mot_trouve = cursor.fetchone()
    temps = round(time.time() - timeStart, 2)

    # Fonction qui met à jour
    conn.commit()

    # Fermeture de la connexion à la base de données
    if verbose:
        print("\n\n---- DECONNEXION BDD ----\n")
    conn.close()

    return mot_trouve, temps


# Fonction qui retourne les mots trouvés,
# le temps que cela a pris ainsi que le nom de la relation associé
def rechercheDumpBDDComplet(mot, type='', verbose=0):

    # Recherche du mot dans la base de données
    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()
    #print(mot)

    timeStart = time.time()

    if type == '':
        cursor.execute(
            """
            SELECT reseau_dump.eid, terme, node2, name, relations_sortantes.type
            FROM reseau_dump, relations_sortantes, entries
            WHERE terme = ?
            AND relations_sortantes.node1 = reseau_dump.eid
            AND entries.eid = relations_sortantes.node2
            AND relations_sortantes.w NOT LIKE '-%'
            """, (mot, ))
    else:
        cursor.execute(
            """
            SELECT reseau_dump.eid, reseau_dump.terme, relations_sortantes.node2, entries.name, relations_sortantes.type
            FROM reseau_dump, relations_sortantes, entries
            WHERE reseau_dump.terme = ?
            AND reseau_dump.eid = relations_sortantes.node1
            AND relations_sortantes.node2 = entries.eid
            AND relations_sortantes.type = ?
            AND relations_sortantes.w NOT LIKE '-%'
            """, (
                mot,
                type,
            ))

    mot_trouve = list(set(cursor.fetchall()))
    if verbose :
        print(mot_trouve)
    temps = round(time.time() - timeStart, 2)

    # Recherche de la relation
    nom_relation = ""
    if type != '':

        #print(type)
        cursor.execute(
            """
            SELECT rtid, trname
            FROM relation_types
            WHERE rtid = ?
            """ , (type,))

        nom_relation = cursor.fetchone()
        #print("nom_relation ", nom_relation)

    conn.commit()
    if verbose:
        print("\n\n---- DECONNEXION BDD ----\n")
    conn.close()

    return mot_trouve, temps, nom_relation


    
# Fonction qui renvoie vrai si la relation mot1 type mot2 est vrai sinon faux sinon jdm ne sais pas [None]
def rechercheRelationVrai(mot1, type, mot2, verbose=0) :

    # Insertion des mots si jamais c'est pas déjà fait
    parseur.insertionDumpBDD(mot1)
    parseur.insertionDumpBDD(mot2)
    
    # Recherche du mot dans la base de données
    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()
    #print(mot)

    timeStart = time.time()

    # Recherche de si la relation est vrai donc si il n'y a pas de - dans poids
    cursor.execute(
        """
        SELECT *
        FROM relations_entrantes
        WHERE node2 = (SELECT eid FROM reseau_dump WHERE terme = ?)
        AND node1 = (SELECT eid FROM reseau_dump WHERE terme = ?)
        AND relations_entrantes.w NOT LIKE '-%'
        AND type = ?
        """, (mot1, mot2, type, )
    )

    mot_trouve_vrai = list(set(cursor.fetchall()))
    if verbose:
        print("mot_trouve_vrai : ", mot_trouve_vrai)
    temps1 = round(time.time() - timeStart, 2)

    # Si on trouve quelque chose alors la relation est vrai
    if mot_trouve_vrai != [] :
        conn.commit()
        if verbose:
            print("\n\n---- DECONNEXION BDD ----\n")
        conn.close()
        return True
    else :
        # Recherche si c'est faux donc si - dans le poids
        cursor.execute(
            """
            SELECT *
            FROM relations_entrantes
            WHERE node2 = (SELECT eid FROM reseau_dump WHERE terme = ?)
            AND node1 = (SELECT eid FROM reseau_dump WHERE terme = ?)
            AND relations_entrantes.w LIKE '-%'
            AND type = ?
            """, (mot1, mot2, type, )
        )
    
        mot_trouve_faux = list(set(cursor.fetchall()))
        if verbose:
            print("mot_trouve_faux : ", mot_trouve_faux)
        temps2 = round(time.time() - timeStart, 2)

        # Si on trouve quelque chose alors la relation est faux
        if mot_trouve_faux != [] :
            conn.commit()
            if verbose:
                print("\n\n---- DECONNEXION BDD ----\n")
            conn.close()
            return False
        # Sinon JDM ne sait pas
        else :
            conn.commit()
            if verbose:
                print("\n\n---- DECONNEXION BDD ----\n")
            conn.close()
            return None

            
# Fonction qui regarde quelle relation est vrai et laquelle est fausse
def demander_a_JDM(mot1, mot2, type_comparaison, type_negation, mot_pronom, mot_verbe, verbose=0) :

    # if verbose:
    #     print("mot1 : ", mot1)
    #     print("mot2 : ", mot2)
    #     print("mot3 : ", mot_verbe)

    # Recherche des mot dans la base
    conn = sqlite3.connect("databases/phrase_courante.db")
    cursor = conn.cursor()

    mot_verbe_origine = mot_verbe

    # Récuperation du verbe à l'infinitif
    cursor.execute("""SELECT nom 
        FROM noeuds, aretes 
        WHERE aretes.id_pere = ? 
        AND aretes.id_fils = id 
        AND aretes.type_relation = ?
        """
        , (mot_verbe, 'r_lemma', ))
    result = cursor.fetchone()
    mot_verbe = result[0] if result else ""

    cursor.execute("SELECT nom FROM noeuds WHERE id = ?", (mot1, ))
    result = cursor.fetchone()
    mot1 = result[0] if result else ""

    cursor.execute("SELECT nom FROM noeuds WHERE id = ?", (mot2, ))
    result = cursor.fetchone()
    mot2 = result[0] if result else ""

    

    # On commit les changements
    conn.commit()
    conn.close()

    if verbose:
        print("mot1 : ", mot1)
        print("mot2 : ", mot2)
        print("mot3 : ", mot_verbe)
    
    reponseA = rechercheRelationVrai(mot1, type_comparaison, mot_verbe, verbose=verbose)
    reponseB = rechercheRelationVrai(mot2, type_comparaison, mot_verbe, verbose=verbose)
    if verbose:
        print("reponseA : ", reponseA)
        print("reponseB : ", reponseB)

    conn = sqlite3.connect("databases/phrase_courante.db")
    cursor = conn.cursor()
    
    if reponseA:
        if reponseB:
            # TODO Recuperer les poids soit par une novuelle recherche soit dans la reponse de rechercheRelationVrai
            if verbose:
                print("On regarde les poids lequel est le meilleur")
        
        else: # Cas où B==Faux ou B==None
            if verbose:
                print("On negative mot_pronom relation mot2")
            # on négative l'arête de B
            print(mot_pronom, type_negation, mot2)
            cursor.execute("""
                UPDATE aretes
                SET poids = ?
                WHERE id_pere = ?
                AND id_fils IN (SELECT id FROM noeuds WHERE nom = ?) 
                AND type_relation = ?
            """, (-1, mot_pronom, mot2, type_negation))
            # # On ajoute une relation r_non pour dire que c'est negatif
            # cursor.execute("""
            #     INSERT OR IGNORE INTO aretes (id_pere, id_fils, type_relation)
            #     VALUES (?, ?, ?)
            #     """, (mot_pronom,
            #           mot2,
            #           'r_non'))
            
            if verbose:
                print("On garde la relation avec mot1")
    else:
        if reponseB:
            if verbose:
                print("On negative mot1 relation mot_verbe")
            # on négative l'arête de A
            print(mot_pronom, type_negation, mot1)
            cursor.execute("""
                UPDATE aretes
                SET poids = ?
                WHERE id_pere = ?
                AND id_fils IN (SELECT id FROM noeuds WHERE nom = ?) 
                AND type_relation = ?
            """, (-1, mot_pronom, mot1, type_negation))
            # # On ajoute une relation r_non pour dire que c'est negatif
            # cursor.execute("""
            #     INSERT OR IGNORE INTO aretes (id_pere, id_fils, type_relation)
            #     VALUES (?, ?, ?)
            #     """, (mot_pronom,
            #           mot1,
            #           'r_non'))

            if verbose:
                print("On garde la relation avec mot2")
            
        elif reponseB == False: # différent de = None
            if verbose:
                print("2 On negative mot2 relation mot_verbe")
            # on négative l'arête de B
            print(mot_pronom, type_negation, mot2)
            cursor.execute("""
                UPDATE aretes
                SET poids = ?
                WHERE id_pere = ?
                AND id_fils IN (SELECT id FROM noeuds WHERE nom = ?) 
                AND type_relation = ?
            """, (-1, mot_pronom, mot2, type_negation))
            # # On ajoute une relation r_non pour dire que c'est negatif
            # cursor.execute("""
            #     INSERT OR IGNORE INTO aretes (id_pere, id_fils, type_relation)
            #     VALUES (?, ?, ?)
            #     """, (mot_pronom,
            #           mot2,
            #           'r_non'))

            if verbose:
                print("On garde la relation avec mot1")
        else:
            if verbose:
                print("On fait des inférences pour trouver si un est vrai ou faux ")
                # TODO
    
    # On commit les changements
    conn.commit()
    conn.close()


def visualise_graph(database_path, export_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Créer un graphe dirigé avec NetworkX
    G = nx.DiGraph()

    # Récupérer tous les nœuds de la table 'noeuds'
    cursor.execute("SELECT id, nom, is_mot FROM noeuds")
    noeuds = cursor.fetchall()

    # Ajouter les nœuds au graphe avec une couleur spécifique en fonction de is_mot
    node_colors = ['#4EBF4B' if (is_mot and nom != 'GN:' and nom != 'GV:') else ('#FFB319' if nom=="GN:" else ('#FF2222' if nom=="GV:" else '#4DA6FF')) for _, nom, is_mot in noeuds]
    for (id_noeud, nom_noeud, is_mot), color in zip(noeuds, node_colors):
        G.add_node(id_noeud, nom=nom_noeud, is_mot=is_mot, color=color)

    # Récupérer toutes les arêtes de la table 'aretes'
    cursor.execute("SELECT id_pere, id_fils, type_relation, poids FROM aretes")
    aretes = cursor.fetchall()

    # Ajouter les arêtes au graphe
    for id_pere, id_fils, type_relation, poids in aretes:
        G.add_edge(id_pere, id_fils, type=type_relation, poids=poids)

    # Créer un dictionnaire de noms de nœuds (sans les identifiants) pour l'affichage
    # node_labels = {node_id: G.nodes[node_id].get('nom', str(node_id)) for node_id in G.nodes}
    node_labels = {node_id: f"{G.nodes[node_id].get('nom', str(node_id))}\nID: {node_id}" for node_id in G.nodes}

    # Créer une liste de couleurs pour chaque arête en fonction de son type
    edge_colors = ['red' if (G.edges[edge]['poids'] < 0) else ('blue' if G.edges[edge]['type'] == 'r_pos' else ('#4EBF4B' if (G.edges[edge]['type'] == 'r_succ') else ('#FFB319' if (G.edges[edge]['type'] == 'GN_part_of') else 'black'))) for edge in G.edges]

    edge_styles = ['dashed' if G.edges[edge]['poids'] < 0 else 'solid' for edge in G.edges]

    # Créer un dictionnaire de noms d'arêtes pour l'affichage
    edge_labels = {edge: G.edges[edge]['type'] for edge in G.edges if G.edges[edge]['type'] not in ['r_pos', 'r_succ']}

    # Affichage du graphe avec les noms de nœuds
    plt.figure(figsize=(25, 25))
    pos = nx.spring_layout(G, k=2)
    nx.draw(G, with_labels=True, labels=node_labels, node_color=node_colors, edge_color=edge_colors, style=edge_styles, pos=pos, connectionstyle='arc3,rad=0.05')
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)
    
    # Sauvegarder le graphe
    plt.savefig(export_path)

    # print("Légende :\nNoeuds :")
    # print("Noeud vert : mot de la phrase")
    # print("Noeud orange : Groupe nominal")
    # print("Noeud rouge : Groupes verbal")
    # print("\nArêtes :")
    # print("Arête verte : r_succ")
    # print("Arête bleue : r_pos")
    # print("Arête rouge : arête négativée")
    # print("Arête noire : label sur le graphe")

    # Fermer la connexion à la base de données
    conn.close()




if __name__ == "__main__":

    # conn = sqlite3.connect("databases/phrase_courante.db")
    # cursor = conn.cursor()

    # cursor.execute("""
    #     UPDATE aretes
    #     SET poids = ?
    #     WHERE type_relation = ?
    # """, (-1, "r_lemma"))
    
    # conn.commit()
    # conn.close()
    
    # affichage_tables(["noeuds", "aretes"], close=True)

    # visualise_graph("databases/phrase_courante.db", "graphes/test.png")
    # print("fini")
    # print(rechercheRelationVrai("pomme", '6', "humain", verbose = 1))
    # insertionRelationsDump('4', ['le',  'petit', 'chat', 'boit', 'du', 'lait'], [2, 3, 4, 5,6, 7], verbose=1)

    # parseur.insertionDumpBDD('distribuer')
    # parseur.insertionDumpBDD('facteur')
    
    # Recherche du mot dans la base de données
    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM mots_composes 
        ORDER BY RANDOM() 
        LIMIT 10
        """)
    rows = cursor.fetchall()
    print(list(rows))
    
    conn.commit()
    conn.close()

import sqlite3
import time
import parseur
import fonction_utiles
import database
import os


# Fonction qui va faire des inférences pour savoir si la relation est vrai ou fausse
def deduction(mot1, type, mot2, verbose=0) :

    # Recherche du mot dans la base de données
    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()
    
    # Recherche du premier mot mot1 est ...
    cursor.execute(
        """
        SELECT reseau_dump.eid, reseau_dump.terme, relations_sortantes.node2, entries.name, relations_sortantes.type
        FROM reseau_dump, relations_sortantes, entries
        WHERE reseau_dump.terme = ?
        AND reseau_dump.eid = relations_sortantes.node1
        AND relations_sortantes.node2 = entries.eid
        AND relations_sortantes.type = '6'
        AND relations_sortantes.w <> "-%"
        AND relations_sortantes.w_normed <> "-%"
        """, (mot1, ))

    relation_trouve_mot1 = list(set(cursor.fetchall()))
    if verbose :
        print(relation_trouve_mot1)
        print(mot2, type)

    # Recherche du deuxieme mot : ... relation mot2
    cursor.execute(
        """
        SELECT reseau_dump.eid, reseau_dump.terme, relations_entrantes.node1, entries.name, relations_entrantes.type
        FROM reseau_dump, relations_entrantes, entries
        WHERE reseau_dump.terme = ?
        AND relations_entrantes.w NOT LIKE '-%'
        AND relations_entrantes.type = ?
        AND reseau_dump.eid = relations_entrantes.node2
        AND relations_entrantes.node1 = entries.eid
        """, (mot2, type, ))
    
    relation_trouve_mot2 = list(set(cursor.fetchall()))
    if verbose :
        print(relation_trouve_mot2)

    # Récuperation des entités de chaque relation
    entite_mot1 = [relation_trouve_mot1[i][3] for i in range(len(relation_trouve_mot1))]
    entite_mot2 = [relation_trouve_mot2[i][3] for i in range(len(relation_trouve_mot2))]
    if verbose :
        print(entite_mot1, entite_mot2)
    
    intersection = list(set(fonction_utiles.calculIntersection(entite_mot1, entite_mot2)))

    conn.commit()
    if verbose:
        print("\n\n---- DECONNEXION BDD ----\n")
    conn.close()

    return intersection



# Fonction qui va faire des inférences pour savoir si la relation est vrai ou fausse
def induction(mot1, type, mot2, verbose=0) :

    # Recherche du mot dans la base de données
    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()

    # Recherche du premier mot ... est mot1
    cursor.execute(
        """
        SELECT reseau_dump.eid, reseau_dump.terme, relations_entrantes.node1, entries.name, relations_entrantes.type
        FROM reseau_dump, relations_entrantes, entries
        WHERE reseau_dump.terme = ?
        AND relations_entrantes.w NOT LIKE '-%'
        AND relations_entrantes.type = '6'
        AND reseau_dump.eid = relations_entrantes.node2
        AND relations_entrantes.node1 = entries.eid
        """, (mot1, ))

    relation_trouve_mot1 = list(set(cursor.fetchall()))
    if verbose :
        print(relation_trouve_mot1)

    # Recherche du deuxieme mot ... relation mot2
    cursor.execute(
        """
        SELECT reseau_dump.eid, reseau_dump.terme, relations_entrantes.node1, entries.name, relations_entrantes.type
        FROM reseau_dump, relations_entrantes, entries
        WHERE reseau_dump.terme = ?
        AND relations_entrantes.w NOT LIKE '-%'
        AND relations_entrantes.type = ?
        AND reseau_dump.eid = relations_entrantes.node2
        AND relations_entrantes.node1 = entries.eid
        """, (mot2, type, ))

    relation_trouve_mot2 = list(set(cursor.fetchall()))
    if verbose :
        print(relation_trouve_mot2)

    # Récuperation des entités de chaque relation
    entite_mot1 = [relation_trouve_mot1[i][3] for i in range(len(relation_trouve_mot1))]
    entite_mot2 = [relation_trouve_mot2[i][3] for i in range(len(relation_trouve_mot2))]
    if verbose :
        print(entite_mot1, entite_mot2)

    intersection = list(set(fonction_utiles.calculIntersection(entite_mot1, entite_mot2)))
    if verbose :
        print(intersection)

    conn.commit()
    if verbose:
        print("\n\n---- DECONNEXION BDD ----\n")
    conn.close()

    return intersection
    


if __name__ == "__main__":
    #database.affichage_tables(['entries', 'relations_sortantes'], base='dump', close=True)
    print("\nIntersection de déduction : ", deduction("pomme", '6', "humain"))
    print("\nIntersection de induction : ", induction("pomme", '6', "humain"))

    print("\nIntersection de déduction : ", deduction("humain", '6', "pomme"))
    print("\nIntersection de induction : ", induction("humain", '6', "pomme"))

    # conn = sqlite3.connect("databases/dump.db")
    # cursor = conn.cursor()
    
    # Recherche du premier mot
    # cursor.execute(
    #     """
    #     SELECT reseau_dump.eid, reseau_dump.terme, relations_sortantes.node2, relations_sortantes.type
    #     FROM reseau_dump, relations_sortantes, entries
    #     WHERE reseau_dump.terme = ?
    #     AND entries.eid = relations_sortantes.node2
    #     AND reseau_dump.eid = relations_sortantes.node1
    #     AND relations_sortantes.w > 0
    #     AND relations_sortantes.type = '6'
    #     """, ("humain", ))

    # cursor.execute(
    #     """
    #     SELECT relations_entrantes.w, reseau_dump.eid, reseau_dump.terme, relations_entrantes.node1, relations_entrantes.type
    #     FROM reseau_dump, relations_entrantes, entries
    #     WHERE reseau_dump.terme = ?
    #     AND entries.eid = relations_entrantes.node1
    #     AND reseau_dump.eid = relations_entrantes.node2
    #     AND relations_entrantes.w NOT LIKE '-%'
    #     AND relations_entrantes.type = '6'
    #     """, ("pomme", ))


    # print(list(set(cursor.fetchall())))


    # conn.commit()
    # conn.close()

import time, os
import sqlite3
import database
import parseur


def affichageReseauDump(mot_trouve, mot, temps, nom_relation, id_relation):

    print("\n\n---- AFFICHAGE RESEAU DUMP ----\n")
    if (mot_trouve != []):
        print(f"Terme '{mot}' : \n{mot_trouve[:25]} ...\n")
        print(f"Temps d'exécution : {temps} secondes")
        liste_relation = []
        for mott in mot_trouve:
            liste_relation.append(mott[3].replace("'", ""))
        print("\n\nLISTE des termes cherché par la relation ", nom_relation,
              " : \n", liste_relation[:25])

    elif nom_relation != None:
        print(
            "\n\n", mot,
            f": pas de relation avec la relation {nom_relation[1]} que vous avez demander"
        )
    else:
        print("\n\n", mot, f": aucune relation avec la relation {id_relation}")


def phraseToTab(phrase):
    tab_phrase = phrase.split(" ")
    #print(tab_phrase)
    # Pour signifier la fin de phrase
    for index, tab in enumerate(tab_phrase) :
        # Met tout en minuscule
        tab_phrase[tab_phrase.index(tab)] = tab.lower()
        #print(tab, tab_phrase)
        # Separationdu point du mot
        if "." in tab and "." != tab :
            tab_phrase[tab_phrase.index(tab)] = tab.replace('.', '')
            tab_phrase.insert(index+1, ".")
    #print(tab_phrase)

    return tab_phrase


def calculIntersection(ens1, ens2):
    return list(set(ens1).intersection(ens2))


# Fonction qui traduit les relations écrites en chiffres vers leurs traductions pour ReseauASK
def traductionChiffreToRelation(mot):
    mot = mot.lower().strip()
    print(mot)

    dictionnaire = {
        '0': ["r_associated"],
        '6': ["r_isa"],
        '9': ["r_has_part"],
        '13': ["r_agent"],
        '24': ["r_agent-1"],
        '14': ["r_patient"],
        '26': ["r_patient-1"],
        '41': ["r_has_conseq"],
        '15': ["r_lieu"],
        '7': ["r_anto"],
        '28': ["r_lieu-1"],
        '42': ["r_has_causatif"],
        '106': ["r_has_color"],
    }
    for (id, relations) in dictionnaire.items():
        for relation in relations:
            if relation == mot:
                return id

    relation = input(f"{relation} Veuillez donner une bonne relation (CtoR) :")
    return traductionChiffreToRelation(relation)
    


if __name__ == "__main__":
    liste1 = [1, 2, 3, 4, 5]
    liste2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # print(calculIntersection(liste1, liste2))
    
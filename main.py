import database
import parseur
import time, os, sys
import sqlite3
import fonction_utiles
import regles
import reponses

if __name__ == "__main__":

    VERBOSE = 0            # Si on veut tous les affichages
    VISUALISE_GRAPH = 1    # Si on veut visualiser le graphe
    DELETE_DATABASE = 0    # Si on veut effacer toute la base

    print("\n--------------------------------------")
    print("--------------------------------------\n\n")

    ###################
    ## MISE EN PLACE ##
    ###################

    # regarder si le fichier databases/ existe
    if not os.path.exists("databases/"):
        os.makedirs("databases/")
        DELETE_DATABASE = 1

    if DELETE_DATABASE :
        try:
            os.remove("databases/dump.db")
            os.remove("databases/phrase_courante.db")
            os.remove("databases/phrase_historique.db")
        except:
            pass
    
        database.create_database()
        time_database = time.time()
        database.insert_mots_composes()
        print(f"\nTemps dajout des mots composés : {round(time.time() - time_database, 2)} s.")
    

    time_delete = time.time()

    liste_table = ['aretes', 'noeuds']
    database.supressionLigne(liste_table, "phrase_courante", verbose=VERBOSE)
    database.affichage_tables(liste_table)
    print(f"Temps de clean de la base : {round(time.time() - time_delete, 2)} s.\n")

    phrase = "?"
    if len(sys.argv) > 1:
        phrase = sys.argv[1]
        
    if phrase == "0" :
        phrase = "Le petit chat boit du lait"
    if phrase == "1" :
        phrase = "Le petit chat roux boit du lait frais"
    elif phrase == "2" :
        phrase = "Le petit facteur mange. Il distribue le courrier"
    elif phrase == "3" :
        phrase = "La petite fille mange du pain. Elle le prend avec les mains"
    elif phrase == "4" :
        phrase = "Jean regarde Tom. Il a peur"
    elif phrase == "5" :
        phrase = "je tu il elle nous vous ils elles"

    elif len(sys.argv) < 2 :
        phrase = input("\nEntrez une phrase : ")

    
    ###################
    ##    Parsing    ##
    ###################

    time_start = time.time()
    time_parseur = time.time()
    
    tab_phrase = fonction_utiles.phraseToTab(phrase)
        
    
    if VERBOSE:
        print("Tab_phrase : ", tab_phrase)
    # Récupereration des id de la table d'origine
    tab_id_phrase = database.insertPhraseToBDD(tab_phrase, verbose=VERBOSE)
    # Enlève les id de START et END
    tab_id_phrase = tab_id_phrase[1:-1]
    if VERBOSE:
        print("Tab_phrase : ", tab_phrase)
        print("Tab_id_phrase : ", tab_id_phrase)

    print(f"Temps de parsing : {round(time.time() - time_parseur, 2)} s.\n")
    
    #####################
    ##    Insertion    ##
    #####################
    
    time_ajout = time.time()
    # Recuperer les r_pos de chacun
    database.insertionRelationsDump('4', tab_phrase, tab_id_phrase, verbose=VERBOSE)
    # Recuperer les r_lemme de chacun
    database.insertionRelationsDump('19', tab_phrase, tab_id_phrase, verbose=VERBOSE)

    database.affichage_tables(["noeuds", "aretes"], close=True)
    print(f"Temps de insertion de la base : {round(time.time() - time_ajout, 2)} s.")

    
    ##################
    ##    Règles    ##
    ##################

    time_regles = time.time()

    fichier_regles = "txt/regles.txt"
    if len(sys.argv) > 2 :
        if sys.argv[2] == "2":
            fichier_regles = "txt/regles_test2.txt"
        else:
            fichier_regles = "txt/regles.txt"
    
    liste_regles = regles.parser_regles(fichier_regles)
    
    if VERBOSE:
        print(f"\n\nRegles à appliquer ({fichier_regles}):")
        for cle, valeur in liste_regles.items():
            print(f"\nstrate {cle} :")
            for corps, tete in valeur:
                print(f"{corps}\n=>\n{tete}\n")
                
    regles.appliquer_regles_sur_noeuds(liste_regles, verbose=0)

    # database.affichage_tables(["noeuds", "aretes"], close=True)

    print(f"Temps d'application des règles : {round(time.time() - time_regles, 2)} s.")

    ################################
    ##    Visualisation graphe    ##
    ################################
    
    print("Remation sémantiques :")
    reponses.reponseProgramme()


    if VISUALISE_GRAPH:
        
        if not os.path.exists("graphes/"):
            os.makedirs("graphes/")

        time_graph = time.time()
        print(f"\nVsualisation du graphe...")
        chemin_graphe = f"graphes/{phrase.replace(' ', '_')}.png"
        database.visualise_graph("databases/phrase_courante.db", chemin_graphe)
        print(f"Graphe généré dans {chemin_graphe} ({round(time.time() - time_graph, 2)}s)\n")


    ##########################
    ##    Réponse finale    ##
    ##########################

    # Donner une réponse
    # print("Votre phrase est sympa.")
    
    
    
    print(f"\n\nTemps total du programme : {round(time.time() - time_start, 2)} s.")
    print("--------------------------------------")
    print("--------------------------------------\n")
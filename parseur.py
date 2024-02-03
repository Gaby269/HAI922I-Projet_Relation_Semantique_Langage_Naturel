import requests
import database
import sqlite3
import re


# Focntion qui met sous forme de graphe des phrases
def phraseToGraphe(phr):

    liste_termes = re.findall(
        r'\w+|[.,!?;]',
        phr)  # un ou plusieurs caracteres alphanumerique + ponctuation

    # Construction des noeud mots par mots
    liste_noeud = []
    terme0 = Noeud([], liste_termes[0], False)  # terme 0
    liste_noeud.append(terme0)
    for m in liste_termes[1:]:
        noeud = Noeud([], m, (m == liste_termes[-1]))
        liste_noeud[liste_termes.index(m) - 1].ajoutSuivant(
            noeud.getId())  # ajoute le noeud à ces suivants
        liste_noeud.append(noeud)  #ajout du noeud dans la liste des noeud

    return liste_noeud


# Focntion qui permet de créer un noeud pour chaque terme mis en paramètre
def motToNoeud(mot, suivants, isFin):
    terme = Noeud(suivants, mot, isFin)
    return terme


# Fonction qui permet de créer une liste de noeud du graphe à partir du milieu d'un mot composé
def milieuPhraseToGraphe(milieuPhrase, noeud_precedent):

    print("[LISTE] liste des termes", milieuPhrase)
    # Construction des noeud mots par mots
    liste_noeud = [noeud_precedent]
    terme0 = noeud_precedent  # noeud de base est le noeud précédent

    # Pour chaque terme de laliste
    for index_m, m in enumerate(milieuPhrase):
        #print(index_m, m)
        noeud = Noeud(
            [], m,
            (m == milieuPhrase[-1]))  # creation du noeud sans ses suivants
        liste_noeud.append(noeud)  #ajout du noeud dans la liste des noeud
        #print("Liste des mots : ", liste_noeud[index_m].getMot())
        liste_noeud[index_m].ajoutSuivant(
            noeud.getId())  # ajoute le noeud à ces suivants
        print("[FOCNTION] Liste des noeuds suivants : ",
              liste_noeud[index_m].getSuivant())

    return liste_noeud


# Créez une instance de la classe
#objet = MaClasse("Mon objet")

# Utilisez la méthode de la classe
#objet.afficher_nom()


# Formatage du texte en dico
def formaterMotsComposes(verbose=0):

    # Liste des données extraite
    liste_mots_composes_id = []
    liste_mots_composes = []
    liste_mc_graphe = []
    liste_termes = []

    chemin_fichier = "txt/mots-composés.txt"

    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        lignes = fichier.readlines()

    lignes_mots_composes = [
        ligne.strip() for ligne in lignes if not ligne.startswith("//")
    ]

    cpt = 0

    for ligne in lignes_mots_composes:

        ligne_split = [mot.strip('";') for mot in ligne.split(";")]
        if len(ligne_split) == 3:
            id = int(ligne_split[0])
            terme = ligne_split[1]
            terme_formate = ligne_split[2]

            mot = {"id": id, "terme": terme, "terme_formate": terme_formate}
            liste_mots_composes.append(terme)
            #print(terme)

            # if cpt < 15:
            #     cpt += 1
            # else:
            #     break

            liste_mots_composes_id.append(mot)

    #liste_mots_composes : liste de dictionnaire de chaque mot composé son id et son terme formaté
    #liste_termes : liste des mots composés sans rien

    liste_noeud_existe = [
    ]  # [mot_courant, position_mc, noeud_graphe, mot_compose_entier]
    liste_mot_compose_contenu = []

    # - Boucle 1 : Prendre le premier mot composé ==> lait de chèvre
    for indice_mc, mot_compose in enumerate(liste_mots_composes):

        # indice_mc = indice du mot compose actuel
        # mot_compose = mot compose reel
        print(f"\n\n[INDICE] Indice MC {indice_mc}: Élément -> {mot_compose}")

        # Transformation du mot composé en tableau
        list_mot = re.findall(r'\w+|[.,!?;]', mot_compose)
        print("[LISTE] Liste des mots : ", list_mot)

        # - Boucle 2 : Parcourir se mot composé pour prendre le premier mot du mc ==> lait
        for indice_mot, mot in enumerate(list_mot):

            # indice_mot = indice du mot courant parmis le mot compose
            # mot = mot courant parmis le mot composé
            print(f"\n [INDICE] Indice MOT {indice_mot}: Élément -> {mot}")

            # - Comparer avec la liste des termes déjà existant dans le graphe pour savoir si le noeud existe déjà ==> lait existe dans liste_noeud_existe à la position i
            is_existe = False
            noeud_existe = [
            ]  # Noeud qui existe dans la liste des noeud existant
            for noeud_liste in liste_noeud_existe:
                if noeud_liste[0] == mot and noeud_liste[1] == indice_mot + 1:
                    print("[COMMENTAIRE] existe deja")
                    is_existe = True
                    noeud_existe = noeud_liste  # noeud qui existe déjà
                    break
                # else:
                #     #print("existe pas")
            print("[COMMENTAIRE] Existe ? ", is_existe)

            # - Si le mot est nouveau alors ==> lait n'est pas dans la liste
            if not is_existe:
                print("[COMMENTAIRE] Il est nouveau")
                # - Appliquer la fonction qui crée la liste des nœuds associé au mc entier
                liste_noeud_graphe_courant = phraseToGraphe(mot_compose)
                #print(liste_noeud_graphe_courant)

                # - Ajouter à la liste liste_noeud_existe chaque mot ==> liste_noeud_existe.append(['lait', 1, graphe[0], 'lait de chèvre'])
                # (le quatrième et si jamais il y a un mot du mc qui est à la meme place que le meme mot dans un autre mc mais qui a le meme noeud mais normalement il y a le noeud qui differencie donc a voir))
                # liste_noeud_existe.append(['de', 2, graphe[1]])
                # liste_noeud_existe.append(['chèvre', 3, graphe[2]])
                for indice_noeud, noeud in enumerate(
                        liste_noeud_graphe_courant):
                    # TODO voir si on ajoute vmt le mot composé entier pour pouvoir recup
                    liste_noeud_existe.append([
                        list_mot[indice_noeud], indice_noeud + 1,
                        liste_noeud_graphe_courant[indice_noeud], mot_compose
                    ])
                    if verbose :
                        print([
                        list_mot[indice_noeud], indice_noeud + 1,
                        liste_noeud_graphe_courant[indice_noeud], mot_compose
                    ])

                # - Passe au mot composé suivant puisqu'on à tout fait ==> lait d'ammande
                break
            # - Sinon le mot a deja été vu ==> lait existe dans la liste à la position 1
            else:
                print("\n[COMMENTAIRE] Il n'est pas nouveau")
                # - Trouver le noeud qui existe déjà
                print("[NOEUD] Noeud qui existe : ", noeud_existe)
                noeud_courant = noeud_existe[2]
                print("[NOEUD] Noeud courant : ", noeud_courant.getMot(),
                      noeud_courant)

                # - Prendre la liste de ses suivants
                suivant_courant = noeud_courant.getSuivant()
                print("[LISTE] Liste des suivant du noeud '",
                      noeud_courant.getMot(), "' : ", suivant_courant)
                # Creation de la boucle des noeuds suivants
                liste_suivant_nom = []
                for id_s in suivant_courant:
                    for noeud in liste_noeud_existe:
                        if noeud[2].getId() == id_s:
                            liste_suivant_nom.append(noeud[0])
                print("[LISTE] Liste des suivants par nom : ",
                      liste_suivant_nom)

                # Récupération des mots suivants
                mot2 = None
                print(len(list_mot) - 1, indice_mot + 1)
                if (len(list_mot) - 1 >= indice_mot + 1):
                    mot2 = list_mot[indice_mot + 1]

                # - Si la liste des suivants est vide
                if suivant_courant == []:
                    print(
                        "[COMMENTAIRE] ----- Liste des suivants vide alors le mot est égal -----"
                    )
                    # - On est arrivé à la fin du mot et tout est egal c'est le même mot composé ( on ne fait rien )
                    # - On passe au suivant de mc  (break)
                    break

                # - Si le mot suivant n'est pas dans la liste des suivants => "de" n'apartient pas à la liste_suivant_lait
                elif mot2 not in liste_suivant_nom:
                    print("[COMMENTAIRE] ----- Le mot '", mot2,
                          "' n'est pas dans la liste des suivants -----")
                    # - Creation du noeud ==> creation du noeud "de" motToNoeud("de", [], liste_mot.index(liste_mot["de"] == liste_mot.lenght-1));
                    noeud_courant_suivant = motToNoeud(
                        mot2, [],
                        len(list_mot) - 1 == indice_mot + 1)
                    print("[NOEUD] Noeud courant suivant de '", mot, "' : ",
                          noeud_courant_suivant)
                    print("[NOEUD] Noeud courant suivant de '", mot,
                          "' par nom : ", noeud_courant_suivant.getMot())
                    print("[NOEUD] Noeud courant suivant de '", mot,
                          "' par id : ", noeud_courant_suivant.getId())
                    print("[NOEUD] Noeud courant suivant de '",
                          mot, "' par suivant : ",
                          noeud_courant_suivant.getSuivant())
                    # - Ajout à la liste des noeud existant
                    liste_noeud_existe.append([
                        mot2, indice_mot + 2, noeud_courant_suivant,
                        mot_compose
                    ])
                    print("[LISTE] AJout dans la liste des noeud existant : ",
                          [
                              mot2, indice_mot + 2, noeud_courant_suivant,
                              mot_compose
                          ])

                    # - Ajout au suivant du mot précédant le mot actuel ==> noeud = 3ème colonne de la liste d'index liste_noeud_existe[i][0] == "lait" ; ajout du noeud "de" au suivant de "lait"
                    noeud_courant.ajoutSuivant(noeud_courant_suivant.getId())
                    print(
                        f"[LISTE] Liste des suivants de noeud_courant {noeud_courant.getMot()} : ",
                        noeud_courant.getSuivant())

                    # - On va creer tous les autres noeuds des mots du mc après "de" car ils seront tous nouveau et à la suite
                    print("[LISTE] Liste des mots suivants : ",
                          list_mot[indice_mot + 2:])
                    suite_noeud = []
                    if list_mot[indice_mot + 2:] != []:
                        print("[NOEUD] Noeud precedent : ",
                              noeud_courant_suivant.getMot())
                        suite_noeud = milieuPhraseToGraphe(
                            list_mot[indice_mot + 2:], noeud_courant_suivant)
                        print("[LISTE] Suite des noeud : ", suite_noeud)
                    else:
                        print(
                            "[COMMENTAIRE] On est arrivé à la fin de la liste des mots du mc"
                        )

                    # Ajout des noeud dans la liste des noeud existant
                    for indice_noeud, noeud in enumerate(suite_noeud[1:]):
                        print(
                            f"\n[INDICE] Indice N {indice_noeud}: Élément -> {noeud.getMot()}"
                        )
                        # TODO voir si on ajoute vmt le mot composé entier pour pouvoir recup
                        liste_noeud_existe.append([
                            noeud.getMot(), indice_mot + 2 + indice_noeud,
                            suite_noeud[indice_noeud + 1], mot_compose
                        ])
                        print("[LISTE] : ", [
                            noeud.getMot(), indice_mot + 2 + indice_noeud,
                            suite_noeud[indice_noeud + 1], mot_compose
                        ])

                    # - On passe au mc suivant (break)
                    break

                # - Sinon la liste des suivants n'est pas vide et que mot2 est dans la liste des suivant de mot1 => tant que "de" (suivant[i].getNom()) est dans la liste de "lait"
                else:
                    # - On continue le parcourt des mots du mc
                    print(
                        "[COMMENTAIRE] ----- Le noeud suivant est égal et rien d'autre -----"
                    )
                    continue

    return True


# Fonction qui cherche dans reseauDUMP en fonctions des infos données
# Le but est de refaire cette fnction en utilisant la base de données plutot que les ficheirs txt
def insertionDumpBDD(mot,
                     id_relation=-1,
                     verbose=0):

    # Recherche du bot dans la base de données
    if verbose:
        print("\n\n---- CONNEXION BDD ----\n")
    #print(mot)
    conn = sqlite3.connect("databases/dump.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT eid, terme, definition FROM reseau_dump
        WHERE terme = ?
        """, (mot, ))
    mot_trouve = cursor.fetchone()

    # Si le mot a deja été trouvé
    if mot_trouve != None:
        if verbose:
            print(f" Le mot '{mot}' est déjà présent en base de données")
        return

    # Si le mot a pas deja été trouvé
    else:

        id = ""
        if (id_relation != -1):
            id = str(id_relation)

        url1 = "https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=" + mot + "&rel=" + id + "&relin=norelin"
        url2 = "https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=" + mot + "&rel=" + id + "&relout=norelout"

        if verbose :
            print(url1)
            print(url2)

        selected1 = "MUTED_PLEASE_RESEND"
        selected2 = "MUTED_PLEASE_RESEND"
        while ("MUTED_PLEASE_RESEND" in selected1 or "MUTED_PLEASE_RESEND" in selected2):

            response1 = requests.get(url1)
            response2 = requests.get(url2)

            # Recuperation des données de reseauDump dans body
            body1 = response1.text
            body2 = response2.text

            # Recherche de la position de la première occurrence de la balise <CODE> pour récuperer les choses à l'interieur
            start_index1 = body1.find("<CODE>")
            start_index2 = body2.find("<CODE>")

            # Recuperation du texte du code source
            selected1 = ""
            selected2 = ""

            # Si le mot existe dans la base
            if start_index1 != -1:
                end_index1 = body1.find("</CODE>", start_index1)
                end_index2 = body2.find("</CODE>", start_index2)

                if end_index1 != -1:
                    # Extraction du contenu entre les balises <CODE> et </CODE>
                    selected1 = body1[start_index1+6:end_index1] # On rajoute la longueur de la balise <CODE>
                    selected2 = body2[start_index2+6:end_index2]

            # Sinon on regarde s'il y a un message d'erreur qui dit que le mot n'existe pas
            else:
                start_index_warning = body1.find(u"""<div class="jdm-warning">""")
                if start_index_warning != -1:
                    print(f"\nLe mot {mot} n'existe pas veuillez changer la phrase")
                else:
                    print("\nErreur lors de la requête")
                exit(1)

        body1 = selected1[:-7]
        body2 = selected2[selected2.find("// les relations entrantes"):]
        #print(body1, body2)
        lignes = [ligne for ligne in (body1.split("\n") + body2.split("\n")) if (ligne.strip() != "")]
        #print(lignes)
        
        print("DEBUT dico")
        donnees_par_categorie = {}
        
        categorieActuelle = "None"  # dans quelle categorie on est
        numCategorie = 0  # id de la categorie
        dansLaBalise = False  # ex : dans <def></def>
        definition = ""  # la definition du mot
        id_entites = []

        eid = int(lignes[0].split('=')[1].strip(') '))  # id du mot

        for ligne in lignes:
            
            if dansLaBalise:  # On igonre les lignes <def></def>, et si on est dedans on cherche
                if ligne.strip() == "</def>":
                    dansLaBalise = False
                else:
                    definition += ligne.strip()
                continue

            elif ligne.strip() == "<def>":
                dansLaBalise = True
                continue

            elif ligne.startswith('//') and (
                    not ":" in ligne):  # Si c'est une ligne de commentaire
                continue

            elif ligne.startswith('//'):
                # on peut regardant tant qu'on a pas start par r
                if (len(
                        donnees_par_categorie.get(categorieActuelle, [])
                ) == 0) and (
                        len(donnees_par_categorie) > 0
                ):  # si la categorie est vide alors on saute le commentaire
                    continue

                # Sinon on a trouvé une nouvelle catégorie
                elif ("les relations sortantes" not in ligne) and (
                        numCategorie == 3
                ):  # on verifie que si jamais ya pas de relations sortantes on incremente
                    # cela veut dire quon est en relations entrantes et que il n'y a pas de relations sortantes
                    numCategorie += 1
                    categorieActuelle = str(numCategorie) + ";" + (
                        ligne.split(":")[1]
                    ).strip(
                    )  # on peut prendre les meme chose que la ligne suivante
                    donnees_par_categorie[categorieActuelle] = []
                    # on passe a la categorie suivante normalement
                    numCategorie += 1
                    categorieActuelle = str(numCategorie) + ";" + (
                        ligne.split(":")[1]
                    ).strip(
                    )  # on peut prendre les meme chose que la ligne suivante
                    donnees_par_categorie[categorieActuelle] = []

                elif ("les relations entrantes" not in ligne) and (
                        numCategorie
                        == 4):  # on regarde si ya des relations entrantes
                    # cela veut dire quon est en relations entrantes mais que yen a pas
                    numCategorie += 1
                    categorieActuelle = str(numCategorie) + ";" + (
                        ligne.split(":")[1]
                    ).strip(
                    )  # on peut prendre les meme chose que la ligne suivante
                    donnees_par_categorie[categorieActuelle] = []

                else:  # sinon on est dans les sortantes et ya pas de problème
                    numCategorie += 1
                    categorieActuelle = str(numCategorie) + ";" + (
                        ligne.split(":")[1]).strip()
                    donnees_par_categorie[categorieActuelle] = []

            # Si la ligne n'est pas un commentaire, on ajoute la ligne à la catégorie courante
            else:
                if categorieActuelle != "None":
                    ligne_courante = ligne.strip().split(';')
                    
                    if len(ligne_courante) < 6 :
                        if ligne_courante[0] == 'r' :
                            continue

                    # Filtre sur les mots inutiles
                    #print(ligne_courante)
                    if ligne_courante[0] == 'e':
                        if ">" not in ligne_courante[2] and "'en:" not in ligne_courante[
                                2] and "'an:" not in ligne_courante[
                                    2] and "'bn:" not in ligne_courante[
                                        2] and "':r" not in ligne_courante[
                                            2] and "'wiki:" not in ligne_courante[
                                                2] and "'umls:" not in ligne_courante[
                                                    2] and "'dbnary:" not in ligne_courante[
                                                        2]:
                            if ":" in ligne_courante[2]:
                                #print(ligne_courante[2])
                                #mot_nouveau = ligne_courante[2].replace("'", "").split(":")[1]
                                if "+" not in ligne_courante[2] : 
                                # print("mot_nouveau", mot_nouveau)
                                #if ligne_courante[2].replace("'", "").split(
                                #       ":")[0] == "Adj" or mot_nouveau == '':
                                    donnees_par_categorie[
                                        categorieActuelle].append(ligne_courante)
                                    id_entites.append(ligne_courante[1])
                                    #print("ligne_courante", ligne_courante)
                            else:
                                donnees_par_categorie[
                                    categorieActuelle].append(ligne_courante)
                                id_entites.append(ligne_courante[1])
                    # Filtre des relations avec les mots inutiles
                    elif ligne_courante[0] == 'r':
                        if ligne_courante[2] in id_entites or ligne_courante[
                                3] in id_entites:
                            donnees_par_categorie[categorieActuelle].append(
                                ligne_courante)
                            #print(ligne_courante)
                    # Sinon on s'en fiche
                    else:
                        donnees_par_categorie[categorieActuelle].append(
                            ligne_courante)

        # SUPPRESSION des type d'entites inutiles
        if verbose :
            print("Supression entités inutiles")
        #print(donnees_par_categorie)

        if "2;e;eid;'name';type;w;'formated name'" in donnees_par_categorie.keys() :
            entites = donnees_par_categorie["2;e;eid;'name';type;w;'formated name'"]
            #print(entites)
            type_entite = []
            [
                type_entite.append(entites[i][3]) for i in range(len(entites))
                if entites[i][3] not in type_entite
            ]
            #print("type_entite", type_entite)
            if "1;nt;ntid;'ntname'" in donnees_par_categorie.keys() :
                type = donnees_par_categorie["1;nt;ntid;'ntname'"]
    
            new_type = []
            for type_courant in type:
                #print("\n", type_courant, type_courant[1])
                if type_courant[1] in type_entite:
                    new_type.append(type_courant)
    
            donnees_par_categorie["1;nt;ntid;'ntname'"] = new_type
        # print("\n", donnees_par_categorie["1;nt;ntid;'ntname'"])
        # print("\nTaille de différence : ",len(donnees_par_categorie["1;nt;ntid;'ntname'"]), len(type))

        # SUPPRESSION des type de relations inutiles
        #print(donnees_par_categorie.keys())
        if "5;r;rid;node1;node2;type;w" not in donnees_par_categorie.keys() :
            donnees_par_categorie["5;r;rid;node1;node2;type;w"] = []

        
        if "4;r;rid;node1;node2;type;w;w_normed;rank" in donnees_par_categorie.keys() :
            if "5;r;rid;node1;node2;type;w" in donnees_par_categorie.keys() :
                relations = donnees_par_categorie[
                "4;r;rid;node1;node2;type;w;w_normed;rank"] + donnees_par_categorie[
                    "5;r;rid;node1;node2;type;w"]
                type_relation = []
                [
                    type_relation.append(relations[i][4])
                    for i in range(len(relations))
                    if relations[i][4] not in type_relation
                ]
                #print("type_relation", type_relation)
                if "3;rt;rtid;'trname';'trgpname';'rthelp'" in donnees_par_categorie.keys() :
                    type = donnees_par_categorie["3;rt;rtid;'trname';'trgpname';'rthelp'"]
            
                    new_type = []
                    for type_courant in type:
                        if type_courant[1] in type_relation:
                            new_type.append(type_courant)
                    donnees_par_categorie["3;rt;rtid;'trname';'trgpname';'rthelp'"] = new_type
            
                # Tri par poids
                relations_trie_4 = sorted(
                    donnees_par_categorie["4;r;rid;node1;node2;type;w;w_normed;rank"],
                    key=lambda x: x[6],
                    reverse=True)
                relations_trie_5 = sorted(
                    donnees_par_categorie["5;r;rid;node1;node2;type;w"],
                    key=lambda x: x[5],
                    reverse=True)
                # Reatribuer la liste trié
                donnees_par_categorie["4;r;rid;node1;node2;type;w;w_normed;rank"] = relations_trie_4
                donnees_par_categorie["5;r;rid;node1;node2;type;w"] = relations_trie_5

        # Format de donnees_par_categorie :
        # {
        #     "1;node_types": [
        #         ["1", "1", "nom"],
        #         ["2", "2", "verbe"]
        #     ],
        #     "2;entries": [
        #         ["1", "1", "bonjour", "nom", "1", "bonjour"],
        #         ["2", "2", "salut", "nom", "1", "salut"]
        #     ],
        #     "3;relation_types": [
        #         ["1", "1", "synonyme", "synonyme", "synonyme"],
        #         ["2", "2", "antonyme", "antonyme", "antonyme"]
        #     ],
        #     "4;relations_sortantes": [
        #         "r;527056043;1921;14453437;71;25"
        #         "r;434445845;215547;14453437;0;17"
        #     ],
        #     "5;relations_entrantes": [
        #         ["r","366801626","14453437","171870","4","41"],
        #         ["2", "2", "3", "1", "1", "1"]
        #     ]
        # }

        if verbose:
            print("\nÉcriture en base de données")

        conn = sqlite3.connect("databases/dump.db")
        cursor = conn.cursor()

        # écriture du mot en base de données

        cursor.execute(
            """
            INSERT INTO reseau_dump(eid, terme, definition) VALUES(?, ?, ?)
            """, (eid, mot, definition.replace("<br />", '\n').strip()))

        # Ecriture des relations en base de données
        #print(donnees_par_categorie)
        for categorie, donnees in donnees_par_categorie.items():
            
            if categorie.startswith("1;"):
                for data in donnees:
                    cursor.execute(
                        """
                        INSERT INTO node_types(ntid, ntname) VALUES(?, ?)
                        """, (data[1], data[2]))

            elif categorie.startswith("2;"):
                for data in donnees:
                    formated_name = data[5] if len(data) > 5 else ''
                    cursor.execute(
                        """
                            INSERT INTO entries(eid, name, type, w, formated_name) VALUES(?, ?, ?, ?, ?)
                            """,
                        (data[1], data[2], data[3], data[4], formated_name))

            elif categorie.startswith("3;"):
                for data in donnees:
                    cursor.execute(
                        """
                        INSERT INTO relation_types(rtid, trname, trgpname, rthelp) VALUES(?, ?, ?, ?)
                        """, (data[1], data[2], data[3], data[4]))

            elif categorie.startswith("4;"):
                for data in donnees:
                    cursor.execute(
                        """
                        INSERT INTO relations_sortantes(rid, node1, node2, type, w, w_normed, rank) VALUES(?, ?, ?, ?, ?, ?, ?)
                        """, (data[1], data[2], data[3], data[4], data[5], data[6], data[7]))

            elif categorie.startswith("5;"):
                for data in donnees:
                    cursor.execute(
                        """
                        INSERT INTO relations_entrantes(rid, node1, node2, type, w) VALUES(?, ?, ?, ?, ?)
                        """, (data[1], data[2], data[3], data[4], data[5]))

        conn.commit()

        print(f"\nLes données du mot \"{mot}\" ont été récupérées.\n\n")

        # Fermeture de la connexion
        if verbose:
            print("\n\n---- DECONNEXION BDD ----\n")
        conn.close()





if __name__ == "__main__":

    liste_table = ['reseau_dump', 'node_types', 'entries', 'relation_types', 'relations_sortantes', 'relations_entrantes']
    database.supressionLigne(liste_table, "dump", verbose=1)
    insertionDumpBDD("miroir", verbose=1)
    #database.affichage_tables(["reseau_dump", "entries", "relations_sortantes"], 'dump',  close=True)

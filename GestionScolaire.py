import flet as ft
from flet import *
from Actions import create_table_etudiant, create_table_option,create_table_filiere,create_table_matiere,create_table_epreuve
import sqlite3
import re
from Tabledonnées import mytable,tb,calldb
from Tabledonnéefilière import mytablefiliere,tbfiliere,calldbfiliere
from Tabledonéeoption import mytableoption,tboption,calldboption
from Tableaudonnéematiere import mytablematiere,tbmatiere,calldbmatiere
from Tabledonéeepreuve import mytableepreuve,tbepreuve,calldbepreuve
import matplotlib
import matplotlib.pyplot as plt
from flet.matplotlib_chart import MatplotlibChart

matplotlib.use("svg")

# Etablir une connection
connexion = sqlite3.connect('GestionScolaire_utf8.db', check_same_thread=False)

def main(page:ft.page):
    page.title = "Gestion de Scolarité"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.auto_scroll = True
    page.scroll = ft.ScrollMode.HIDDEN
    page.appbar = ft.AppBar(
        title=ft.Text(
            "MALEZI", weight=ft.FontWeight.BOLD, color=ft.colors.PINK
        ),
        bgcolor=ft.colors.BLACK,   
        color=ft.colors.WHITE,
    )
        
    #Exécuter le script pour créer la table lors du premier lancement
    create_table_filiere()
    create_table_option()
    create_table_etudiant()
    create_table_matiere()
    create_table_epreuve()
      
    page.scroll = "auto"
    
    #permet d'afficher le formulaire de l'etudiant
    def showInput(e):
        inputcon.offset =  transform.Offset(0,0)
        page.update()
    
    #cacher le formulaire de l'éetudiant
    def hidecon(e):
       inputcon.offset =  transform.Offset(2,0)
       page.update()
       
    def savedata(e):
        try:
            # Récupéreration du nom de la filière/ l'intitulé de l'option sélectionnée
            nom_filiere = filiere_etudiant.value
            intitule_option = option.value
            
             # Vérification de la condition pour le champ "Email"
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email.value):
                # Affichage d'un message d'erreur
                page.snack_bar = SnackBar(
                    Text("Veuillez entrer une adresse email valide"), bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return  # Arrêt de la fonction si la condition n'est pas satisfaite
            
            # Vérification de la condition pour le champ "Numéro de téléphone"
            if not re.match(r'^(06|07)\d{8}$', num_tel.value):
                # Affichage d'un message d'erreur
                page.snack_bar = SnackBar(
                    Text("Veuillez entrer un numéro de téléphone valide (06 ou 07 suivi de 8 chiffres)"), bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return  # Arrêt de la fonction si la condition n'est pas satisfaite
            
            # Récupéreration de l'ID correspondant au nom du filière
            cursor = connexion.cursor()
            cursor.execute('SELECT "id_filière" FROM "filiere" WHERE "nom_filiere" = ?', (nom_filiere,))
            result = cursor.fetchone()
            if result:
                filiere_id = result[0]
            else:
                # Affichage d'un message d'erreur si la filière n'est pas trouvée
                page.snack_bar = SnackBar(
                    Text("La filière spécifiée n'a pas été trouvée"), bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return  # Arrêt de la fonction si la filière n'est pas trouvée
                
            # Récupéreration de l'ID correspondant à l'intitulé de l'option
            cursor = connexion.cursor()
            cursor.execute('SELECT code_option FROM "option" WHERE "intitulé" = ?', (intitule_option,))
            result = cursor.fetchone()
            if result:
                option_id = result[0]
            else:
                # Affichage d'un message d'erreur si la filière n'est pas trouvée
                page.snack_bar = SnackBar(
                    Text("L'option' n'a pas été trouvée"), bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return  # Arrêt de la fonction si la filière n'est pas trouvée

                
            #insertion dans la base de donnée
            cursor = connexion.cursor()
            cursor.execute("""INSERT INTO etudiant (prenom, nom, addresse, numéro_tel, genre,code_option, age, email, id_filière)
                           VALUES (?, ?, ?, ?, ?, ?, ?,?,?)""",
               (prenom.value, nom.value, addresse.value, num_tel.value, genre.value,option_id,age.value, email.value, filiere_id))
            connexion.commit()
            print("succès")
            
            # Réinitialiser le formulaire après l'enregistrement
            prenom.value = ""
            nom.value = ""
            addresse.value = ""
            num_tel.value = ""
            genre.value = ""
            option.value = ""
            age.value = ""
            email.value = ""
            filiere_etudiant.value = ""
              
            #Glisser vers la droite à nouveau si l'entrée finale réussit
            inputcon.offset =  transform.Offset(2,0)
            #Ajouter une notification (snackbar) en cas de succès de l'ajout dans la base de données.
            page.snack_bar = SnackBar (
                Text("Enregistrer avec succès"),bgcolor="green"
            )
            page.snack_bar.open = True
            page.update()
            
        except Exception as e:
            print(e)

# Exécution de cette requête SQL pour récupérer les noms des filieres de la table "filiere"
    def recupnomofiliere():
        cursor = connexion.cursor()
        cursor.execute('SELECT "id_filière", "nom_filiere" FROM "filiere"')
        result = cursor.fetchall()
        # Récupéreration des valeurs de la colonne "intitulé" et associer les codes d'option
        filieres = {row[1]: row[0] for row in result}
        return filieres
       
# Exécution de cette requête SQL pour récupérer les intitulés de la table "option"
    def recupnomoption():
        cursor = connexion.cursor()
        cursor.execute('SELECT code_option, "intitulé" FROM "option"')
        result = cursor.fetchall()
        # Récupéreration des valeurs de la colonne "intitulé" et associer les codes d'option
        options = {row[1]: row[0] for row in result}
        return options
    
    # Appele de la fonction pour récupérer les options et filières depuis la base de données
    options = recupnomoption()
    filieres = recupnomofiliere()

    # Création d'une liste d'objets ft.dropdown.Option avec l'intitulé et 
    # le code_option/le nom et l'id associé  associé pour chaque option/filières
    dropdown_options = [ft.dropdown.Option(option, option) for option in options]
    dropdown_filieres = [ft.dropdown.Option(filiere, filiere) for filiere in filieres]

    #création d'un fichier pour la saisie des données
    prenom = TextField(label="Prenom")
    nom = TextField(label="Nom")
    addresse = TextField(label="Addresse")
    num_tel = TextField(label="Numéro de télephone")
    genre =RadioGroup(content = Column([
        Radio(value = "H", label = "Homme"),
        Radio(value = "F", label = "femme")
    ]))
    option = Dropdown(label="Option", options=dropdown_options)
    age = TextField(label="Age")
    email = TextField(label="Email")
    filiere_etudiant = Dropdown(label="Filière", options=dropdown_filieres)
     
    #Creation d'un modele pour l'ajout d'un nouveau etudiant 
    inputcon = Card (
        #Ajouter un effet de glissement vers la gauche
        offset = transform.Offset(2,0),
        animate_offset = animation.Animation(600,curve = "easeIn"),
        elevation=30,
        content = Container(
            bgcolor = ft.colors.WHITE12,
            padding = 15,
            border_radius = 20,
            content = Column([
                Row([
                Text("Nouveau étudiant", size=20, weight="bold"),
                IconButton(icon = "close", icon_size=20, on_click=hidecon),
                ]),
                   prenom,
                   nom,
                   addresse,
                   num_tel,
                   genre,
                   option,
                   age,  
                   email,
                   filiere_etudiant,
                   FilledButton("sauvegarder", 
                   on_click=savedata)     
            ])
        )
    ) 
    
    #Insertion des filiere dans la base 
    #-----------------------------------
    #Afficher le formulaire pour ajouter une option
    def showOptionInput(e):
        optionInputCon.offset = transform.Offset(0, 0)
        page.update()
    
    #Cacher le formulaire
    def hideOptionInput(e):
        optionInputCon.offset = transform.Offset(2, 0)
        page.update()
        
    def saveoption(e):
        try:
            nom_filiere = filiere.value
            # Récupéreration de l'ID correspondant au nom du filière
            cursor = connexion.cursor()
            cursor.execute('SELECT id_filière FROM "filiere" WHERE "nom_filiere" = ?', (nom_filiere,))
            result = cursor.fetchone()
            if result:
                filiere_id = result[0]
          #insertion dans la base de donnée
            cursor = connexion.cursor()
            cursor.execute("""INSERT INTO option (intitulé,durée, id_filière)
                           VALUES (?, ?, ?)""",
               (intitulé.value.upper(),duree.value, filiere_id))
            connexion.commit()
            print("succès")
            # Réinitialisation du formulaire de la filière
            intitulé.value = ""
            duree.value = ""
            
            # Masquer le formulaire de la filière
            optionInputCon.offset = transform.Offset(2, 0)
            
            # Afficher une notification de succès
            page.snack_bar = SnackBar(
                Text("Enregistré avec succès"), bgcolor="green"
            )
            page.snack_bar.open = True
            page.update()
        
        except Exception as e:
             print(e)
    
    # Création du formulaire pour l'ajout d'une nouvelle option
    intitulé = TextField(label="Nom de l'option")
    duree = TextField(label="Nombre d'heure de l'option")
    filiere = Dropdown(label="Filière", options=dropdown_filieres)
    
    #carte d'affichage du fomulaire
    optionInputCon = Card(
        offset=transform.Offset(2, 0),
        animate_offset=animation.Animation(600, curve="easeIn"),
        elevation=30,
        content=Container(
            bgcolor=ft.colors.WHITE12,
            padding=15,
            border_radius=20,
            content=Column([
                Row([
                    Text("Nouvelle option", size=20, weight="bold"),
                    IconButton(icon="close", icon_size=20, on_click=hideOptionInput),
                ]),
                intitulé,
                duree,
                filiere,
                FilledButton("Sauvegarder", on_click=saveoption),
            ])
        )
    )
    
   #Filiere insertion database
    def showFiliereInput(e):
        filiereInputCon.offset = transform.Offset(0, 0)
        page.update()
    
    #Cacher le formulaire
    def hideFiliereInput(e):
        filiereInputCon.offset = transform.Offset(2, 0)
        page.update()
        
    def savefiliere(e):
        try:
          #insertion dans la base de donnée
            cursor = connexion.cursor()
            cursor.execute("""INSERT INTO filiere(nom_filiere,nombre_semetre)
                           VALUES (?, ?)""",
               (nom_du_filiere.value,semestres.value))
            connexion.commit()
            print("succès")
            # Réinitialisation du formulaire de la filière
            nom_du_filiere.value = ""
            semestres.value = ""
            
            # Masquer le formulaire de la filière
            filiereInputCon.offset = transform.Offset(2, 0)
            
            # Afficher une notification de succès
            page.snack_bar = SnackBar(
                Text("Enregistré avec succès"), bgcolor="green"
            )
            page.snack_bar.open = True
            page.update()
        
        except Exception as e:
             print(e)
    
    # Création du formulaire pour l'ajout d'une nouvelle filière
    nom_du_filiere = TextField(label="Nom de la filière")
    semestres = TextField(label="Nombre de semestre")
    
    filiereInputCon = Card(
        offset=transform.Offset(2, 0),
        animate_offset=animation.Animation(600, curve="easeIn"),
        elevation=30,
        content=Container(
            bgcolor=ft.colors.WHITE12,
            padding=15,
            border_radius=20,
            content=Column([
                Row([
                    Text("Nouvelle filière", size=20, weight="bold"),
                    IconButton(icon="close", icon_size=20, on_click=hideFiliereInput),
                ]),
                nom_du_filiere,
                semestres,
                FilledButton("Sauvegarder", on_click=savefiliere),
            ])
        )
    )
    
    #Afficher le formulaire pour ajouter une matière
    def showmatiereInput(e):
        matiereInputCon.offset = transform.Offset(0, 0)
        page.update()
    
    #Cacher le formulaire
    def hidematiereInput(e):
        matiereInputCon.offset = transform.Offset(2, 0)
        page.update()
        
    def saveomatiere(e):
        try:
            option_matiere = optionmatiere.value
            # Récupéreration de l'ID correspondant à l'intitulé de l'option
            cursor = connexion.cursor()
            cursor.execute('SELECT code_option FROM "option" WHERE "intitulé" = ?', (option_matiere,))
            result = cursor.fetchone()
            if result:
                option_id = result[0]
          #insertion dans la base de donnée
          
            cursor = connexion.cursor()
            cursor.execute("""INSERT INTO matiere (code_option,nom_matiere, coefficient)
                           VALUES (?, ?, ?)""",
               (option_id,nom_matiere.value.upper(), coef.value))
            connexion.commit()
            print("succès")
            # Réinitialisation du formulaire de la filière
            nom_matiere.value = ""
            coef.value = ""
            
            # Masquer le formulaire de la filière
            matiereInputCon.offset = transform.Offset(2, 0)
            
            # Afficher une notification de succès
            page.snack_bar = SnackBar(
                Text("Enregistré avec succès"), bgcolor="green"
            )
            page.snack_bar.open = True
            page.update()
        
        except Exception as e:
             print(e)
    
    # Création du formulaire pour l'ajout d'une nouvelle option
    nom_matiere = TextField(label="Nom de la matière")
    optionmatiere =Dropdown(label="Options", options=dropdown_options)
    coef = TextField(label="Coefficient de la matière")
    
    matiereInputCon = Card(
        offset=transform.Offset(2, 0),
        animate_offset=animation.Animation(600, curve="easeIn"),
        elevation=30,
        content=Container(
            bgcolor=ft.colors.WHITE12,
            padding=15,
            border_radius=20,
            content=Column([
                Row([
                    Text("Nouvelle matière", size=20, weight="bold"),
                    IconButton(icon="close", icon_size=20, on_click=hidematiereInput),
                ]),
                nom_matiere,
                optionmatiere,
                coef ,
                FilledButton("Sauvegarder", on_click=saveomatiere),
            ])
        )
    )
  
#Afficher le formulaire pour ajouter une epreuve
    def showepreuveInput(e):
        epreuveInputCon.offset = transform.Offset(0, 0)
        page.update()
    
    #Cacher le formulaire
    def hideepreuveInput(e):
        epreuveInputCon.offset = transform.Offset(2, 0)
        page.update()
        
    def saveepreuve(e):
        try:
            matiereepreuve = matiere_epreuve.value
            etudiant = etudiant_epreuve.value
            # Récupéreration de l'ID correspondant à l'intitulé de la matière
            cursor = connexion.cursor()
            cursor.execute('SELECT id_matiere FROM "matiere" WHERE "nom_matiere" = ?', (matiereepreuve,))
            result = cursor.fetchone()
            if result:
                matière_id = result[0]    
          
          # Récupéreration de l'ID correspondant au nom de l'étudiant
            cursor = connexion.cursor()
            cursor.execute('SELECT id_etudiant FROM "etudiant" WHERE "prenom" = ?', (etudiant,))
            result = cursor.fetchone()
            if result:
                etudiant_id = result[0]  
              
            #insertion dans la base de donnée  
            cursor = connexion.cursor()
            cursor.execute("""INSERT INTO epreuve (id_matiere,id_etudiant, date_epreuve,note,type)
                           VALUES (?, ?, ?,?,?)""",
               (matière_id ,etudiant_id, date_epreuve.value, note.value, type_matiere.value.upper()))
            connexion.commit()
            print("succès")
            
            # Masquer le formulaire de la filière
            epreuveInputCon.offset = transform.Offset(2, 0)
            
            # Afficher une notification de succès
            page.snack_bar = SnackBar(
                Text("Enregistré avec succès"), bgcolor="green"
            )
            page.snack_bar.open = True
            page.update()
        
        except Exception as e:
             print(e)
    
    # Exécution de cette requête SQL pour récupérer les noms des filieres de la table "filiere"
    def recupnomatiere():
        cursor = connexion.cursor()
        cursor.execute('SELECT id_matiere, "nom_matiere" FROM "matiere"')
        result = cursor.fetchall()
        # Récupéreration des valeurs de la colonne "intitulé" et associer les codes d'option
        matieres = {row[1]: row[0] for row in result}
        return matieres
       
  # Exécution de cette requête SQL pour récupérer les etudiant de la table "etudiant"
    def recupnometudiant():
        cursor = connexion.cursor()
        cursor.execute('SELECT id_etudiant, "prenom" FROM "etudiant"')
        result = cursor.fetchall()
        # Récupéreration des valeurs de la colonne "intitulé" et associer les codes d'option
        etudiants = {row[1]: row[0] for row in result}
        return etudiants
    
    # Appele de la fonction pour récupérer les options et filières depuis la base de données
    matieres = recupnomatiere()
    etudiants = recupnometudiant()
    
    # Création d'une liste d'objets ft.dropdown.Option avec l'intitulé et 
    # le code_option/le nom et l'id associé  associé pour chaque option/filières
    dropdown_matieres= [ft.dropdown.Option(matiere, matiere) for matiere in matieres]
    dropdown_etudiants  = [ft.dropdown.Option(etudiant, etudiant) for etudiant in etudiants]
    
    # Création du formulaire pour l'ajout d'une nouvelle option
    matiere_epreuve = Dropdown(label="Matière", options=dropdown_matieres)
    etudiant_epreuve=Dropdown(label="Etudiants", options=dropdown_etudiants)
    date_epreuve = TextField(label="Date de l'épreuve")
    note = TextField(label="Note")
    type_matiere = TextField(label="Type d'épreuve")
    
    epreuveInputCon = Card(
        offset=transform.Offset(2, 0),
        animate_offset=animation.Animation(600, curve="easeIn"),
        elevation=30,
        content=Container(
            bgcolor=ft.colors.WHITE12,
            padding=15,
            border_radius=20,
            content=Column([
                Row([
                    Text("Nouvelle epreuve", size=20, weight="bold"),
                    IconButton(icon="close", icon_size=20, on_click=hideepreuveInput),
                ]),
                matiere_epreuve,
                etudiant_epreuve,
                date_epreuve,
                note,
                type_matiere,
                FilledButton("Sauvegarder", on_click=saveepreuve),
            ])
        )
    )
    
    def generate_graph():
    # Récupérez les données
        cursor = connexion.cursor()
        cursor.execute('SELECT age, moyenne FROM etudiant')  # Remplacez par votre requête SQL appropriée
        data = cursor.fetchall()
    
    # Séparez les données en deux listes (âge et moyenne)
        age = [row[0] for row in data]
        moyenne = [row[1] for row in data]

    # Créez le graphe
        plt.figure()
        plt.plot(age, moyenne, 'o')  # Utilisez le type de graphique approprié, par exemple 'o' pour des points
    
        plt.xlabel('Âge')
        plt.ylabel('Moyenne')
        plt.title('Graphe d\'analyse des étudiants')

    # Affichez le graphe
        plt.show()
    generate_graph()
    page.add(
        
    Column([
        Row([
            ElevatedButton("Nouveau étudiant", on_click=showInput, bgcolor=ft.colors.PINK, color="white"),
            ElevatedButton("Nouveau filière", on_click=showFiliereInput, bgcolor=ft.colors.PINK, color="white"),
            ElevatedButton("Nouvelle option", on_click=showOptionInput, bgcolor=ft.colors.PINK, color="white"),
            ElevatedButton("Nouvelle matière", on_click=showmatiereInput, bgcolor=ft.colors.PINK, color="white"),
            ElevatedButton("Nouvelle epreuve", on_click=showepreuveInput, bgcolor=ft.colors.PINK, color="white"),
           
        ]),
        mytable,
        mytableoption,
        mytablefiliere,
        mytablematiere,
        mytableepreuve,
        
        #Boîte de dialogue pour ajouter des données
        inputcon, # Formulaire d'ajout de l'etudiant
        filiereInputCon,  # Formulaire d'ajout de filière
        optionInputCon,# Formulaire d'ajout de l'option
        matiereInputCon,# Formulaire d'ajout de la matière
        epreuveInputCon,# Formulaire d'ajout de la matière
        #notification si on obtient une erreur
        # désactiver l'importation de datatable 
    ]),     
)

ft.app(target=main, view=WEB_BROWSER)
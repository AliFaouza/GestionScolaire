from flet import *
import flet as ft
import sqlite3

connexion = sqlite3.connect('GestionScolaire_utf8.db', check_same_thread=False)

tb = DataTable(
    columns = [
        DataColumn(Text("Etudiants")),
        DataColumn(Text("Prenom")),
        DataColumn(Text("Nom")),
        DataColumn(Text("Adresse")),
        DataColumn(Text("Num_tel")),
        DataColumn(Text("Genre")),
        DataColumn(Text("Option")),
        DataColumn(Text("email")),
        DataColumn(Text("Age")),
        DataColumn(Text("Filière")),
        
    ],
    rows =[]
)

# Exécution de cette requête SQL pour récupérer les noms des filieres de la table "filiere"
def recupnomofiliere():
        cursor = connexion.cursor()
        cursor.execute('SELECT id_filière, "nom_filiere" FROM "filiere"')
        result = cursor.fetchall()
        # Récupéreration des valeurs de la colonne "intitulé" et associer les codes d'option
        filieres = {row[1]: row[0] for row in result}
        return filieres
    
 # Exécution de cette requête SQL pour récupérer les intitulés de la table "option"   
def recupnomoption():
        cursor = connexion.cursor()
        cursor.execute('SELECT code_option, "intitulé" FROM "option"')
        result = cursor.fetchall()
        # Récupérer les valeurs de la colonne "intitulé" et associer les codes d'option
        options = {row[1]: row[0] for row in result}
        return options
    
# Appele de la fonction pour récupérer les options et filières depuis la base de données
filieres = recupnomofiliere()
options = recupnomoption()

# Création d'une liste d'objets ft.dropdown.Option avec l'intitulé et 
# le code_option/le nom et l'id associé  associé pour chaque option/filières
dropdown_options = [ft.dropdown.Option(option, option) for option in options]
dropdown_filieres = [ft.dropdown.Option(filiere, filiere) for filiere in filieres]


#Création d'un champ de texte pour obtenir les données de la ligne sélectionnée en tant que paramètre
id_modif = Text()
prenom_modif = TextField(label="Prenom")
nom_modif = TextField(label="Nom")
addresse_modif= TextField(label="Addresse")
num_tel_modif = TextField(label="Numéro de télephone")
genre_modif =RadioGroup(content = Column([
        Radio(value = "H", label = "Homme"),
        Radio(value = "F", label = "femme")
    ]))
option_modif = Dropdown(label="Option (modif)", options=dropdown_options)
age_modif = TextField(label="Age")
mail_modif = TextField(label="Email")
filiere_modif = Dropdown(label="Filière", options=dropdown_filieres)



def hidedlg(e):
    #Masquer en cas d'annulation de la modification
    dlg.visible = False
    dlg.update()
    
def saveandupdate(e):
    try:
        # Récupération du nom de la filière / de l'intitulé de l'option sélectionnée
        intitule_option = option_modif.value
        nom_filiere = filiere_modif.value
        # Récupération de l'ID correspondant au nom de la filière
        cursor = connexion.cursor()
        
        # Récupérer l'ID correspondant à l'intitulé de l'option
        cursor.execute('SELECT code_option FROM "option" WHERE "intitulé" = ?', (intitule_option,))
        result = cursor.fetchone()
        if result:
            option_id_modif = result[0]

        cursor.execute('SELECT id_filière FROM "filiere" WHERE "nom_filiere" = ?', (nom_filiere,))
        result = cursor.fetchone()
        if result:
            filiere_id_modif = result[0]

        myid = id_modif.value
        cursor.execute("""UPDATE etudiant SET prenom=?, nom=?, addresse=?,
                      numéro_tel=?,genre=?,code_option=?, age=?, email=?, id_filière=? WHERE id_etudiant=?""",
                       (prenom_modif.value, nom_modif.value, addresse_modif.value,
                        num_tel_modif.value, genre_modif.value, option_id_modif, age_modif.value, mail_modif.value,
                        filiere_id_modif, myid))
        connexion.commit()
        print("Modifié avec succès")

        # En cas de succès, rafraîchir le tableau pour mettre à jour les changements
        tb.rows.clear()
        # Pour effacer la ligne, puis ajouter à nouveau depuis SQLite
        calldb()
        # Configurer la fenêtre modale d'édition à faux en cas de succès du changement.
        dlg.visible = False
        dlg.update()
        tb.update()
    except Exception as e:
        print(e)
#Création d'une fenêtre/boîte de dialogue pour effectuer des modifications
dlg = Container(
    bgcolor = ft.colors.AMBER,
    padding = 15,
    border_radius = 20,
    content=Column([
        Row([
        Text("Modification des Données", size = 20, weight = "bold"),
        IconButton(icon= "close", on_click=hidedlg)
        ]),
        #Ajout d'un widget comme un champ texte pour la modification
        prenom_modif,
        nom_modif,
        addresse_modif,
        num_tel_modif,
        Text("Choisir le genre", size=20),
        genre_modif,
        option_modif,
        age_modif,
        mail_modif,
        filiere_modif,
        ElevatedButton("Enregistrer la modification", on_click = saveandupdate),   
    ])
)
def showedit(e):
    
    #Récupération de data=x à partir de ICONBUTTON
    data_edit = e.control.data
    id_modif.value = data_edit['id_etudiant']
    prenom_modif.value = data_edit['prenom']
    nom_modif.value = data_edit['nom']
    addresse_modif.value = data_edit['addresse']
    num_tel_modif.value = data_edit['numéro_tel']
    genre_modif.value = data_edit['genre']
    option_modif.value = data_edit.get('intitulé','')
    age_modif.value = data_edit['age']
    mail_modif.value = data_edit['email']
    filiere_modif.value = data_edit.get('nom_filiere','')
    
    #Affichage d'une fenetre pour la modification
    dlg.visible = True
    dlg.update()

#Exécuter un script pour récupérer toutes les données de la base 
# de données lors du premier lancement de l'application.

def showdelete(e):
    #pour supprimer
    try:
        myid = int(e.control.data)
        cursor = connexion.cursor()
        cursor.execute("DELETE FROM etudiant WHERE id_etudiant=?",(myid,))
        connexion.commit()
        
        #Rafraichir la table pour voir les changements
        tb.rows.clear()
        calldb()
        tb.update()
    except Exception as e:
        print(e)
        
        
def calldb():
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM etudiant")
    etudiant = cursor.fetchall()
    print(etudiant)
    
    #S'il y a des données, alors insérer la table dans la ligne du widget de tableau
    if not etudiant =="":
        keys = ['id_etudiant','prenom','nom','addresse','numéro_tel','genre','code_option','email','age','id_filière']
        #Extraire les données de la table pour les convertir en un dictionnaire en Python.
        result = [dict(zip(keys,values)) for values in etudiant]
        for x in result:
             # Récupérer l'intitulé de l'option correspondant au code_option
            cursor.execute('SELECT "intitulé" FROM "option" WHERE code_option = ?', (x['code_option'],))
            option_result = cursor.fetchone()
            if option_result:
                intitule = option_result[0]
            else:
                intitule = ""
                
             #Récupérer le nom de la filière correspondant du filiere
            cursor.execute('SELECT "nom_filiere" FROM "filiere" WHERE id_filière = ?', (x['id_filière'],))
            filiere_result = cursor.fetchone()
            if filiere_result:
                nom_filiere = filiere_result[0]
            else:
                nom_filiere = ""
                
            #Repeter dans une boucle
            tb.rows.append(
                DataRow(
                    cells = [
                        DataCell(Row([
                            #Création des boutons de modification et de suppression ici
                        IconButton(icon="edit", icon_color="blue", icon_size=20,
                            #Récuperation des données pour les passer à la fonction de modification
                            data=x,
                            on_click=showedit
                            ),
                        
                        IconButton(icon="delete", icon_color="red",icon_size=20, 
                                   data=x['id_etudiant'], 
                                   on_click=showdelete )
                        ])),
                       DataCell(Text(x['prenom'])),
                       DataCell(Text(x["nom"])),
                       DataCell(Text(x["addresse"])),
                       DataCell(Text(x["numéro_tel"])),
                       DataCell(Text(x["genre"])),
                       DataCell(Text(intitule)),
                       DataCell(Text(x["age"])),
                       DataCell(Text(x["email"])),
                       DataCell(Text(nom_filiere)),
                              
                                  
    ]
 )
)
            
#Lancement de la fonction
calldb()

# Création de  la fonctionnalité d'affichage de la modification.
            

#Configuration d'une fenêtre modale pour la modifcation à faux par défaut.   
dlg.visible = False


#Afficher la table
mytable = Column([
    dlg,
    Row([tb], scroll = "always")
])

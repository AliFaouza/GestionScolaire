from flet import *
import flet as ft
import sqlite3

connexion = sqlite3.connect('GestionScolaire_utf8.db', check_same_thread=False)

tboption = DataTable(
    columns = [
        DataColumn(Text("Options")),
        DataColumn(Text("Intitulé")),
        DataColumn(Text("Duréé")),
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
    
# Appele de la fonction pour récupérer les options et filières depuis la base de données
filieres = recupnomofiliere()

# Création d'une liste d'objets ft.dropdown.Option avec l'intitulé et 
# le code_option/le nom et l'id associé  associé pour chaque option/filières
dropdown_filieres = [ft.dropdown.Option(filiere, filiere) for filiere in filieres]

#Création d'un champ de texte pour obtenir les données de la ligne sélectionnée en tant que paramètre
id_modif = Text()
intitule_modif = TextField(label="Intitulé")
duree_modif = TextField(label="Durée")
filiere_modif = Dropdown(label="Filières", options=dropdown_filieres)

def hidedlg(e):
    #Masquer en cas d'annulation de la modification
    dlgoption.visible = False
    dlgoption.update()
    
def updateoption(e):
    try:
        # Récupération du nom de la filière / de l'intitulé de l'option sélectionnée
        nom_filiere = filiere_modif.value
        
        # Récupération de l'ID correspondant au nom de la filière
        cursor = connexion.cursor()
        cursor.execute('SELECT id_filière FROM "filiere" WHERE "nom_filiere" = ?', (nom_filiere,))
        result = cursor.fetchone()
        if result:
            filiere_id_modif = result[0]

        myid = id_modif.value
        cursor.execute("""UPDATE option SET intitulé=?, durée=?, id_filière=? WHERE code_option=?""",
               (intitule_modif.value.upper(), duree_modif.value, filiere_id_modif, myid))
        connexion.commit()
        print("Modifié avec succès")

        # En cas de succès, rafraîchir le tableau pour mettre à jour les changements
        tboption.rows.clear()
        # Pour effacer la ligne, puis ajouter à nouveau depuis SQLite
        calldboption()
        # Configurer la fenêtre modale d'édition à faux en cas de succès du changement.
        dlgoption.visible = False
        dlgoption.update()
        tboption.update()
    except Exception as e:
        print(e)
#Création d'une fenêtre/boîte de dialogue pour effectuer des modifications
dlgoption = Container(
    bgcolor = ft.colors.AMBER,
    padding = 15,
    border_radius = 20,
    content=Column([
        Row([
        Text("Modification des Données", size = 20, weight = "bold"),
        IconButton(icon= "close", on_click=hidedlg)
        ]),
        #Ajout d'un widget comme un champ texte pour la modification
        intitule_modif,
        duree_modif,
        filiere_modif,
        ElevatedButton("Enregistrer la modification", on_click = updateoption),   
    ])
)

def showedit(e):   
    #Récupération de data=x à partir de ICONBUTTON
    data_edit = e.control.data
    id_modif.value = data_edit['code_option']
    intitule_modif.value = data_edit['intitulé']
    duree_modif.value = data_edit['durée']
    filiere_modif.value = data_edit.get('nom_filiere','')
    
    #Affichage d'une fenetre pour la modification
    dlgoption.visible = True
    dlgoption.update()

#Exécuter un script pour récupérer toutes les données de la base 
# de données lors du premier lancement de l'application.

def showdelete(e):
    #pour supprimer
    try:
        myid = int(e.control.data)
        cursor = connexion.cursor()
        cursor.execute("DELETE FROM option WHERE code_option=?",(myid,))
        connexion.commit()
        
        #Rafraichir la table pour voir les changements
        tboption.rows.clear()
        calldboption()
        tboption.update()
    except Exception as e:
        print(e)
        
        
def calldboption():
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM option")
    options = cursor.fetchall()
    print(options)
    
    # S'il y a des données, alors insérer la table dans la ligne du widget de tableau
    if options:
        keys = ['code_option', 'intitulé', 'durée', 'id_filière']
        # Extraire les données de la table pour les convertir en un dictionnaire en Python.
        result = [dict(zip(keys, values)) for values in options]
        for x in result:   
            # Récupérer le nom de la filière correspondant à l'id_filière
            cursor.execute('SELECT "nom_filiere" FROM "filiere" WHERE id_filière = ?', (x['id_filière'],))
            filiere_result = cursor.fetchone()
            if filiere_result:
                nom_filiere = filiere_result[0]
            else:
                nom_filiere = ""
                
            # Répéter dans une boucle
            tboption.rows.append(
                DataRow(
                    cells=[
                        DataCell(Row([
                            # Création des boutons de modification et de suppression ici
                            IconButton(icon="edit", icon_color="blue", icon_size=20,
                                       # Récupération des données pour les passer à la fonction de modification
                                       data=x,
                                       on_click=showedit
                                       ),
                        
                            IconButton(icon="delete", icon_color="red", icon_size=20, 
                                       data=x['code_option'], 
                                       on_click=showdelete)
                        ])),
                        DataCell(Text(x['intitulé'])),
                        DataCell(Text(x["durée"])),
                        DataCell(Text(nom_filiere))
                    ]
                )
            )
            
#Lancement de la fonction
calldboption()

# Création de  la fonctionnalité d'affichage de la modification.
            

#Configuration d'une fenêtre modale pour la modifcation à faux par défaut.   
dlgoption.visible = False


#Afficher la table
mytableoption = Column([
    dlgoption,
    Row([tboption], scroll = "always")
])

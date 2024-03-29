from flet import *
import flet as ft
import sqlite3

connexion = sqlite3.connect('GestionScolaire_utf8.db', check_same_thread=False)

tbmatiere = DataTable(
    columns = [
        DataColumn(Text("Matières")),
        DataColumn(Text("Intitulé")),
        DataColumn(Text("Option")),
        DataColumn(Text("Coef")),
    ],
    rows =[]
)

 # Exécution de cette requête SQL pour récupérer les intitulés de la table "option"   
def recupnomoption():
        cursor = connexion.cursor()
        cursor.execute('SELECT code_option, "intitulé" FROM "option"')
        result = cursor.fetchall()
        # Récupérer les valeurs de la colonne "intitulé" et associer les codes d'option
        options = {row[1]: row[0] for row in result}
        return options
    
# Appele de la fonction pour récupérer les options et filières depuis la base de données
options = recupnomoption()

# Création d'une liste d'objets ft.dropdown.Option avec l'intitulé et 
# le code_option/le nom et l'id associé  associé pour chaque option/filières
dropdown_options = [ft.dropdown.Option(option, option) for option in options]

#Création d'un champ de texte pour obtenir les données de la ligne sélectionnée en tant que paramètre
id_modif = Text()
intitule_modif = TextField(label="Matière")
option_modif = Dropdown(label="Options", options=dropdown_options)
coef_modif = TextField(label="Coefficient")

def hidedlg(e):
    #Masquer en cas d'annulation de la modification
    dlgmatiere.visible = False
    dlgmatiere.update()
    
def updatematiere(e):
    try:
        # Récupération du nom de la filière / de l'intitulé de l'option sélectionnée
        nom_option = option_modif.value
        
        # Récupération de l'ID correspondant au nom de la filière
        cursor = connexion.cursor()
        cursor.execute('SELECT code_option FROM "option" WHERE "intitulé" = ?', (nom_option,))
        result = cursor.fetchone()
        if result:
            optionid_modif = result[0]

        myid = id_modif.value
        cursor.execute("""UPDATE matiere SET nom_matiere=?, code_option=?, coefficient=? WHERE id_matiere=?""",
               (intitule_modif.value.upper(), optionid_modif,coef_modif .value, myid))
        connexion.commit()
        print("Modifié avec succès")

        # En cas de succès, rafraîchir le tableau pour mettre à jour les changements
        tbmatiere.rows.clear()
        # Pour effacer la ligne, puis ajouter à nouveau depuis SQLite
        calldbmatiere()
        # Configurer la fenêtre modale d'édition à faux en cas de succès du changement.
        dlgmatiere.visible = False
        dlgmatiere.update()
        tbmatiere.update()
    except Exception as e:
        print(e)
        
#Création d'une fenêtre/boîte de dialogue pour effectuer des modifications
dlgmatiere = Container(
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
        option_modif,
        coef_modif,
        ElevatedButton("Enregistrer la modification", on_click = updatematiere),   
    ])
)

def showedit(e):   
    #Récupération de data=x à partir de ICONBUTTON
    data_edit = e.control.data
    id_modif.value = data_edit['id_matiere']
    intitule_modif.value = data_edit.get('code_option','')
    coef_modif.value = data_edit['coefficient']
    
    #Affichage d'une fenetre pour la modification
    dlgmatiere.visible = True
    dlgmatiere.update()

#Exécuter un script pour récupérer toutes les données de la base 
# de données lors du premier lancement de l'application.

def showdelete(e):
    #pour supprimer
    try:
        myid = int(e.control.data)
        cursor = connexion.cursor()
        cursor.execute("DELETE FROM matiere WHERE id_matiere=?",(myid,))
        connexion.commit()
        
        #Rafraichir la table pour voir les changements
        tbmatiere.rows.clear()
        calldbmatiere()
        tbmatiere.update()
    except Exception as e:
        print(e)
        
        
def calldbmatiere():
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM matiere")
    matieres = cursor.fetchall()
    print(matieres)
    
    # S'il y a des données, alors insérer la table dans la ligne du widget de tableau
    if matieres:
        keys = ['id_matiere', 'nom_matiere', 'code_option', 'coefficient']
        # Extraire les données de la table pour les convertir en un dictionnaire en Python.
        result = [dict(zip(keys, values)) for values in matieres]
        for x in result:   
            # Récupérer le nom de la filière correspondant à l'id_filière
            cursor.execute('SELECT "intitulé" FROM "option" WHERE code_option = ?', (x['code_option'],))
            option_result = cursor.fetchone()
            if option_result:
                nom_option= option_result[0]
            else:
                nom_option = ""
                
            # Répéter dans une boucle
            tbmatiere.rows.append(
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
                                       data=x['id_matiere'], 
                                       on_click=showdelete)
                        ])),
                        DataCell(Text(x['nom_matiere'])),
                        DataCell(Text(nom_option)),
                        DataCell(Text(x['coefficient']))
                       
                    ]
                )
            )
            
#Lancement de la fonction
calldbmatiere()

# Création de  la fonctionnalité d'affichage de la modification.
            

#Configuration d'une fenêtre modale pour la modifcation à faux par défaut.   
dlgmatiere.visible = False


#Afficher la table
mytablematiere = Column([
    dlgmatiere,
    Row([tbmatiere], scroll = "always")
])

from flet import *
import flet as ft
import sqlite3


connexion = sqlite3.connect('GestionScolaire_utf8.db', check_same_thread=False)

tbfiliere = DataTable(
    columns = [
        DataColumn(Text("Filières")),
        DataColumn(Text("Nom du filère")),
        DataColumn(Text("Nombre_etudiant")),
        DataColumn(Text("Semestres")),
    ],
    rows =[]
)

#Création d'un champ de texte pour obtenir les données de la ligne sélectionnée en tant que paramètre
id_modif = Text()
nom_dufiliere_modif = TextField(label="Filière")
semestres = TextField(label="Semetres")

def hidedlgfiliere(e):
    #Masquer en cas d'annulation de la modification
    dlgfiliere.visible = False
    dlgfiliere.update()
    
def Updatefiliere(e):
    try:
        cursor = connexion.cursor()
        myid = id_modif.value
        cursor.execute("""UPDATE filiere SET nom_filiere=?, nombre_semetre=? WHERE id_filière=?""",
                       (nom_dufiliere_modif.value.upper(),semestres.value, myid))
        connexion.commit()
        print("Modifié avec succès")

        # En cas de succès, rafraîchir le tableau pour mettre à jour les changements
        tbfiliere.rows.clear()
        # Pour effacer la ligne, puis ajouter à nouveau depuis SQLite
        calldbfiliere()
        # Configurer la fenêtre modale d'édition à faux en cas de succès du changement.
        dlgfiliere.visible = False
        dlgfiliere.update()
        tbfiliere.update()
    except Exception as e:
        print(e)
        
#Création d'une fenêtre/boîte de dialogue pour effectuer des modifications
dlgfiliere = Container(
    bgcolor = ft.colors.AMBER,
    padding = 15,
    border_radius = 20,
    content=Column([
        Row([
        Text("Modification des Données", size = 20, weight = "bold"),
        IconButton(icon= "close", on_click=hidedlgfiliere)
        ]),
        #Ajout d'un widget comme un champ texte pour la modification
        nom_dufiliere_modif,
        semestres,
        ElevatedButton("Enregistrer la modification", on_click = Updatefiliere),  
    ])
)

def showedit(e): 
    #Récupération de data=x à partir de ICONBUTTON
    data_edit = e.control.data
    id_modif.value = data_edit['id_filière']
    nom_dufiliere_modif.value = data_edit['nom_filiere']
    semestres.value = data_edit['nombre_semestre']
    #Affichage d'une fenetre pour la modification
    dlgfiliere.visible = True
    dlgfiliere.update()

#Exécuter un script pour récupérer toutes les données de la base 
# de données lors du premier lancement de l'application.

def showdelete(e):
    #pour supprimer
    try:
        myid = int(e.control.data)
        cursor = connexion.cursor()
        cursor.execute("DELETE FROM filiere WHERE id_filière=?",(myid,))
        connexion.commit()
        
        #Rafraichir la table pour voir les changements
        tbfiliere.rows.clear()
        calldbfiliere()
        tbfiliere.update()
    except Exception as e:
        print(e)
        
        
def calldbfiliere():
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM filiere")
    filieres = cursor.fetchall()
    print(filieres)
    
    #S'il y a des données, alors insérer la table dans la ligne du widget de tableau
    if not filieres =="":
        keys = ['id_filière','nom_filiere','nombre_etudiant','nombre_semestre',]
        #Extraire les données de la table pour les convertir en un dictionnaire en Python.
        result = [dict(zip(keys,values)) for values in filieres]
        for x in result:    
            #Repeter dans une boucle pour recupere tous les données
            tbfiliere.rows.append(
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
                                   data=x['id_filière'], 
                                   on_click=showdelete )
                        
                       
                        ])),
                       DataCell(Text(x['nom_filiere'])),
                       DataCell(Text(x['nombre_etudiant'])),
                       DataCell(Text(x["nombre_semestre"])),                           
    ]
 )
)
            
#Lancement de la fonction
calldbfiliere()

# Création de  la fonctionnalité d'affichage de la modification.
        
#Configuration d'une fenêtre modale pour la modification à faux par défaut.   
dlgfiliere.visible = False

#Afficher la table
mytablefiliere = Column([
    dlgfiliere,
    Row([tbfiliere], scroll = "always")
])

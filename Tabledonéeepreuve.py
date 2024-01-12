from flet import *
import flet as ft
import sqlite3

connexion = sqlite3.connect('GestionScolaire_utf8.db', check_same_thread=False)

tbepreuve = DataTable(
    columns = [
        DataColumn(Text("Epreuves")),
        DataColumn(Text("Matière")),
        DataColumn(Text("Etudiant")),
        DataColumn(Text("Date")),
        DataColumn(Text("Note")),
        DataColumn(Text("Type")),
        
    ],
    rows =[]
)

# Exécution de cette requête SQL pour récupérer les noms des filieres de la table "filiere"
def recupnomomatiere():
        cursor = connexion.cursor()
        cursor.execute('SELECT id_matiere, "nom_matiere" FROM "matiere"')
        result = cursor.fetchall()
        # Récupéreration des valeurs de la colonne "intitulé" et associer les codes d'option
        matieres = {row[1]: row[0] for row in result}
        return matieres
    
 # Exécution de cette requête SQL pour récupérer les intitulés de la table "option"   
def recupnoetudiant():
        cursor = connexion.cursor()
        cursor.execute('SELECT id_etudiant, "prenom" FROM "etudiant"')
        result = cursor.fetchall()
        # Récupérer les valeurs de la colonne "intitulé" et associer les codes d'option
        etudiants = {row[1]: row[0] for row in result}
        return etudiants
    
# Appele de la fonction pour récupérer les options et filières depuis la base de données
matieres = recupnomomatiere()
etudiants = recupnoetudiant()

# Création d'une liste d'objets ft.dropdown.Option avec l'intitulé et 
# le code_option/le nom et l'id associé  associé pour chaque option/filières
dropdown_etudiants = [ft.dropdown.Option(etudiant, etudiant) for etudiant in etudiants]
dropdown_matieres = [ft.dropdown.Option(matiere, matiere) for matiere in matieres]

#Création d'un champ de texte pour obtenir les données de la ligne sélectionnée en tant que paramètre
id_modif = Text()
matiere_modif = Dropdown(label="Matiere modif", options=dropdown_matieres)
etudiant_modif = Dropdown(label="Etudiant", options=dropdown_etudiants)
date_modif= TextField(label="Date de l'épreuve")
note_modif= TextField(label="Note")
type_modif= TextField(label="Type")



def hidedlgepreuve(e):
    #Masquer en cas d'annulation de la modification
    dlgepreuve.visible = False
    dlgepreuve.update()
    
def saveandupdate(e):
    try:
        # Récupération du nom de la filière / de l'intitulé de l'option sélectionnée
        matiere = matiere_modif .value
        etudiant = etudiant_modif.value

        # Récupération de l'ID correspondant au nom de la filière
        cursor = connexion.cursor()
        cursor.execute('SELECT id_matiere FROM "matiere" WHERE "nom_matiere" = ?', (matiere,))
        result = cursor.fetchone()
        if result:
            matiere_id_modif = result[0]

        # Récupérer l'ID correspondant à l'intitulé de l'option
        cursor.execute('SELECT id_etudiant FROM "etudiant" WHERE  "prenom" = ?', (etudiant,))
        result = cursor.fetchone()
        if result:
            etudiant_id_modif = result[0]

        myid = id_modif.value
        cursor.execute("""UPDATE epreuve SET id_matiere=?, id_etudiant=?, date_epreuve=?,
                      note=?,type=? WHERE id_epreuve=?""",
                       (matiere_id_modif, etudiant_id_modif, date_modif.value,
                        note_modif.value, type_modif.value, myid))
        connexion.commit()
        print("Modifié avec succès")

        # En cas de succès, rafraîchir le tableau pour mettre à jour les changements
        tbepreuve.rows.clear()
        # Pour effacer la ligne, puis ajouter à nouveau depuis SQLite
        calldbepreuve()
        # Configurer la fenêtre modale d'édition à faux en cas de succès du changement.
        dlgepreuve.visible = False
        dlgepreuve.update()
        tbepreuve.update()
        
    except Exception as e:
        print(e)
        
#Création d'une fenêtre/boîte de dialogue pour effectuer des modifications
dlgepreuve = Container(
    bgcolor = ft.colors.AMBER,
    padding = 15,
    border_radius = 20,
    content=Column([
        Row([
        Text("Modification des Données", size = 20, weight = "bold"),
        IconButton(icon= "close", on_click=hidedlgepreuve)
        ]),
        #Ajout d'un widget comme un champ texte pour la modification
        matiere_modif,
        etudiant_modif,
        date_modif,
        note_modif,
        type_modif,
        ElevatedButton("Enregistrer la modification", on_click = saveandupdate),   
    ])
)
def showedit(e):
    
    #Récupération de data=x à partir de ICONBUTTON
    data_edit = e.control.data
    id_modif.value = data_edit['id_epreuve']
    matiere_modif.value = data_edit.get('nom_matiere','')
    etudiant_modif.value = data_edit.get('prenom','')
    date_modif.value = data_edit['date_epreuve']
    note_modif.value = data_edit['note']
    type_modif.value = data_edit['type']
  
    #Affichage d'une fenetre pour la modification
    dlgepreuve.visible = True
    dlgepreuve.update()

#Exécuter un script pour récupérer toutes les données de la base 
# de données lors du premier lancement de l'application.

def showdelete(e):
    #pour supprimer
    try:
        myid = int(e.control.data)
        cursor = connexion.cursor()
        cursor.execute("DELETE FROM epreuve WHERE id_epreuve=?",(myid,))
        connexion.commit()
        
        #Rafraichir la table pour voir les changements
        tbepreuve.rows.clear()
        calldbepreuve()
        tbepreuve.update()
    except Exception as e:
        print(e)
        
        
def calldbepreuve():
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM epreuve")
    epreuve = cursor.fetchall()
    print(epreuve)
    
    #S'il y a des données, alors insérer la table dans la ligne du widget de tableau
    if not epreuve =="":
        keys = ['id_epreuve','id_matiere','id_etudiant','date_epreuve','note','type']
        #Extraire les données de la table pour les convertir en un dictionnaire en Python.
        result = [dict(zip(keys,values)) for values in epreuve]
        for x in result:
             # Récupérer l'intitulé de l'option correspondant au code_option
            cursor.execute('SELECT "nom_matiere" FROM "matiere" WHERE id_matiere = ?', (x['id_matiere'],))
            matiere_result = cursor.fetchone()
            if matiere_result:
                matiere = matiere_result[0]
            else:
                matiere = ""
                
             #Récupérer le nom de la filière correspondant du filiere
            cursor.execute('SELECT "prenom" FROM "etudiant" WHERE id_etudiant = ?', (x['id_etudiant'],))
            etudiant_result= cursor.fetchone()
            if etudiant_result:
                etudiant = etudiant_result[0]
            else:
                etudiant = ""
                
            #Repeter dans une boucle
            tbepreuve.rows.append(
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
                                   data=x['id_epreuve'], 
                                   on_click=showdelete )
                        ])), 
                        DataCell(Text(matiere)),
                        DataCell(Text(etudiant)),
                        DataCell(Text(x["date_epreuve"])),
                        DataCell(Text(x["note"])),
                        DataCell(Text(x["type"])),                       
                                  
    ]
 )
)
            
#Lancement de la fonction
calldbepreuve()

# Création de  la fonctionnalité d'affichage de la modification.
            
#Configuration d'une fenêtre modale pour la modifcation à faux par défaut.   
dlgepreuve.visible = False

#Afficher la table
mytableepreuve = Column([
    dlgepreuve,
    Row([tbepreuve], scroll = "always")
])

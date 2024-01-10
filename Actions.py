import sqlite3

# Establish a connection
connexion = sqlite3.connect('GestionScolaire_utf8.db', check_same_thread=False)

#ce script permet de créer un automatiquement un tableau filiere quand on lance l'application flet
def create_table_filiere():
    cursor = connexion.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS filiere (
        id_filière INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_filiere TEXT,
        nombre_etudiant NUMERIC ,
        nombre_semetre NUMERIC
        )""")
    connexion.commit()
    
    # Après la création de la table "etudiant", exécuter une requête pour mettre à jour la colonne "nombre_etudiant" dans la table "filiere"
    cursor.execute("""UPDATE filiere
                      SET nombre_etudiant = (
                          SELECT COUNT(*) 
                          FROM etudiant 
                          WHERE etudiant.id_filière = filiere.id_filière
                      )""")
    connexion.commit()

#ce script permet de créer un automatiquement un tableau option quand on lance l'application flet
def create_table_option():
    cursor = connexion.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS option (
        code_option INTEGER PRIMARY KEY AUTOINCREMENT,
        intitulé TEXT,
        durée NUMERIC,
        id_filière INTEGER,
        FOREIGN KEY(id_filière) REFERENCES filiere(id_filière)
        )""")
    connexion.commit()
    
    
#ce script permet de créer un automatiquement un tableau etudiant quand on lance l'application flet
def create_table_etudiant():
    # Create a cursor object
    cursor = connexion.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS etudiant (
        id_etudiant INTEGER PRIMARY KEY AUTOINCREMENT, 
        prenom TEXT, 
        nom TEXT, 
        addresse TEXT, 
        numéro_tel TEXT, 
        genre TEXT, 
        code_option INTEGER, 
        id_filière INTEGER
        age INTEGER, 
        email TEXT, 
        num_etudiant INTEGER,
        moyenne NUMERIC,
        FOREIGN KEY(code_option) REFERENCES option(code_option),
        FOREIGN KEY(id_filière) REFERENCES filiere(id_filière)
        )""")
    connexion.commit()
    
   # Création d'un déclencheur pour incrémenter num_etudiant après chaque insertion
    cursor.execute("""CREATE TRIGGER IF NOT EXISTS increment_num_etudiant
        AFTER INSERT ON etudiant
        BEGIN
            -- Mise à jour de num_etudiant avec la prochaine valeur de la séquence
            UPDATE etudiant
            SET num_etudiant = (SELECT seq FROM sqlite_sequence WHERE name='etudiant') + 1
            WHERE id_etudiant = new.id_etudiant;
        END""")
    connexion.commit()

def create_table_matiere():
    cursor = connexion.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS matiere (
        id_matiere INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_matiere TEXT,
        code_option INTEGER,
        coefficient INTEGER,
        FOREIGN KEY(code_option) REFERENCES option(code_option)
        )""")
    connexion.commit()
    
def create_table_epreuve():
    cursor = connexion.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS epreuve (
        id_epreuve INTEGER PRIMARY KEY AUTOINCREMENT,
        id_matiere INTEGER,
        id_etudiant INTEGER,
        date_epreuve TEXT,
        note NUMERIC,
        type TEXT,
        FOREIGN KEY(id_matiere) REFERENCES matiere(id_matiere),
        FOREIGN KEY(id_etudiant) REFERENCES etudiant(id_etudiant)
        )""")
    connexion.commit()
    
    
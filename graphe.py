import matplotlib
import matplotlib.pyplot as plt
from Actions import create_table_filiere
from flet.matplotlib_chart import MatplotlibChart
import flet as ft
import sqlite3

matplotlib.use("svg")
connexion = sqlite3.connect('GestionScolaire_utf8.db', check_same_thread=False)

def main(page: ft.Page):
    create_table_filiere()
  # Récupération des données
    cursor = connexion.cursor()
    cursor.execute("SELECT nom_filiere, nombre_etudiant FROM filiere")
    rows = cursor.fetchall()

    # Préparation des données
    filieres = []
    nombre_etudiants = []
    for row in rows:
        filieres.append(row[0])
        nombre_etudiants.append(row[1])

    # Analyse des données
    fig, ax = plt.subplots()
    ax.bar(filieres, nombre_etudiants)

    ax.set_ylabel("Nombre d'étudiants")
    ax.set_title("Nombre d'étudiants par filière")

    # Assurez-vous que le nombre d'étiquettes de barre correspond au nombre de barres
    bar_labels = filieres
    bar_colors = ["tab:blue", "tab:purple", "tab:orange", "tab:orange"]
    ax.bar(filieres, nombre_etudiants, label=bar_labels, color=bar_colors)


    page.add(MatplotlibChart(fig, expand=True))


ft.app(target=main)
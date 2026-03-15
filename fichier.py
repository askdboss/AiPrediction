import pandas as pd
import sqlite3

# Connexion à la base (elle se mettra à jour)
conn = sqlite3.connect('supermarche.db')

# Liste de tes fichiers
fichiers = {
    'annex1.csv': 'produits',
    'annex2.csv': 'ventes',
    'annex3.csv': 'stocks',
    'annex4.csv': 'clients'
}

for fichier, nom_table in fichiers.items():
    try:
        df = pd.read_csv(fichier)
        # On injecte chaque fichier dans sa propre table SQL
        df.to_sql(nom_table, conn, if_exists='replace', index=False)
        print(f"✅ {fichier} importé avec succès dans la table '{nom_table}'")
    except Exception as e:
        print(f"❌ Erreur sur {fichier}: {e}")

conn.close()
print("\nBase de données mise à jour avec toutes les annexes !")
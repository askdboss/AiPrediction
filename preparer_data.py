import pandas as pd
import sqlite3

conn = sqlite3.connect('supermarche.db')

# 1. On charge d'abord un petit échantillon pour voir les VRAIS noms des colonnes
ventes_sample = pd.read_sql_query("SELECT * FROM ventes LIMIT 1", conn)
print("Colonnes détectées dans ventes :", ventes_sample.columns.tolist())

# 2. On récupère les noms exacts (on va les copier ici après ton test si ça rate encore)
# Pour l'instant, on va essayer de sélectionner toutes les colonnes (*) 
# pour éviter l'erreur de nom, puis on filtrera avec Pandas.

requete = """
SELECT v.*, p."Item Name", p."Category Name"
FROM ventes v
JOIN produits p ON v."Item Code" = p."Item Code"
WHERE v."Sale or Return" = 'sale'
"""

df_final = pd.read_sql_query(requete, conn)

# 3. Nettoyage : on ne garde que ce qui nous intéresse pour l'IA
# On affiche les colonnes pour que tu puisses vérifier
print("Colonnes après fusion :", df_final.columns.tolist())

# Transformation du Discount en 1 et 0
if 'Discount' in df_final.columns:
    df_final['Discount'] = df_final['Discount'].map({'Yes': 1, 'No': 0})

# 4. Sauvegarde
df_final.to_sql('data_ia', conn, if_exists='replace', index=False)

print("\n✅ Table 'data_ia' créée avec succès !")
conn.close()
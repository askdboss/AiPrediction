import pandas as pd
import sqlite3
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import joblib

# 1. Charger les données depuis la table data_ia
conn = sqlite3.connect('supermarche.db')
df = pd.read_sql_query("SELECT * FROM data_ia", conn)
conn.close()

# 2. Préparation des variables
# 2. Préparation des variables
# On force la conversion du Discount : 'Yes' devient 1, tout le reste (No, NaN, etc.) devient 0
df['Discount (Yes/No)'] = df['Discount (Yes/No)'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)

# On s'assure que le prix est bien un nombre (on enlève les erreurs éventuelles)
df['Unit Selling Price (RMB/kg)'] = pd.to_numeric(df['Unit Selling Price (RMB/kg)'], errors='coerce')
df['Quantity Sold (kilo)'] = pd.to_numeric(df['Quantity Sold (kilo)'], errors='coerce')

# On supprime les lignes vides s'il y en a après la conversion
df = df.dropna(subset=['Unit Selling Price (RMB/kg)', 'Quantity Sold (kilo)'])

X = df[['Unit Selling Price (RMB/kg)', 'Discount (Yes/No)']]
y = df['Quantity Sold (kilo)']

# 3. Division des données : 80% pour l'entraînement, 20% pour le test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Entraînement du modèle
model = LinearRegression()
model.fit(X_train, y_train)

# 5. Prédictions sur le jeu de test (les 20% que l'IA n'a jamais vus)
y_pred = model.predict(X_test)

# 6. Calcul des métriques d'évaluation
r2 = metrics.r2_score(y_test, y_pred) # Précision globale
mae = metrics.mean_absolute_error(y_test, y_pred) # Erreur moyenne en kilos
rmse = np.sqrt(metrics.mean_squared_error(y_test, y_pred)) # Erreur type (pénalise les grosses erreurs)

print("-" * 30)
print("📊 RÉSULTATS DE L'ÉVALUATION")
print("-" * 30)
print(f"R² (Score de corrélation) : {r2:.4f}")
print(f"MAE (Erreur Moyenne Absolue) : {mae:.2f} kg")
print(f"RMSE (Racine de l'erreur quadratique) : {rmse:.2f} kg")
print("-" * 30)

# 7. VERDICT AUTOMATIQUE
print("\n--- VERDICT ---")
if r2 > 0.7:
    print("✅ TRÈS FIABLE : Le modèle explique très bien les variations de ventes.")
elif r2 > 0.4:
    print("⚠️ MOYENNEMENT FIABLE : Le modèle donne une bonne tendance, mais il y a une marge d'erreur.")
else:
    print("❌ PEU FIABLE : Le prix et la promo ne suffisent pas à expliquer les ventes. Il manque peut-être des données (météo, jour férié, etc.).")

# 8. Sauvegarde du modèle
joblib.dump(model, 'modele_supermarche.pkl')
print("\nModèle sauvegardé dans 'modele_supermarche.pkl'")
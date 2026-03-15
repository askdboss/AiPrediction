from flask import Flask, render_template, request
import sqlite3
import joblib
import pandas as pd

app = Flask(__name__)
model = joblib.load('modele_supermarche.pkl')

def get_db_connection():
    conn = sqlite3.connect('supermarche.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    produits_db = conn.execute('SELECT "Item Code", "Item Name" FROM produits').fetchall()
    produits = [{"Item Code": "", "Item Name": "-- Choisir un produit --"}] + [dict(p) for p in produits_db]
    
    # INITIALISATION : On définit des valeurs vides par défaut pour le chargement (GET)
    prediction = None
    profit = None
    alerte = ""
    prix_saisi = 0.0
    item_selectionne = ""
    promo_cochee = 0

    if request.method == 'POST':
        item_selectionne = request.form.get('item_code') # On récupère le choix
        
        if item_selectionne and item_selectionne != "":
            try:
                prix_saisi = float(request.form['prix'])
                promo_cochee = 1 if request.form.get('promo') else 0

                # 2. Chercher les infos du produit
                stock_query = conn.execute('SELECT * FROM stocks WHERE "Item Code" = ? LIMIT 1', (item_selectionne,)).fetchone()
                
                if stock_query:
                    res_dict = dict(stock_query)
                    colonne_prix = [k for k in res_dict.keys() if 'Wholesale' in k]
                    
                    if colonne_prix:
                        prix_achat = res_dict[colonne_prix[0]]
                        
                        # 3. Prédiction IA
                        input_data = pd.DataFrame([[prix_saisi, promo_cochee]], 
                                                  columns=['Unit Selling Price (RMB/kg)', 'Discount (Yes/No)'])
                        
                        res_ia = model.predict(input_data)[0]
                        prediction = round(max(0, res_ia), 2)

                        # 4. Profit
                        profit = round(prediction * (prix_saisi - prix_achat), 2)
                        
                        if profit < 0:
                            alerte = "⚠️ Attention : Vente à perte !"
                    else:
                        alerte = "Erreur : Prix d'achat introuvable."
                else:
                    alerte = "Produit non trouvé en stock."
            except Exception as e:
                alerte = f"Erreur : {str(e)}"

    conn.close()
    
    # On renvoie bien TOUTES les variables au HTML
    return render_template('index.html', 
                           produits=produits, 
                           prediction=prediction, 
                           profit=profit, 
                           alerte=alerte, 
                           prix=prix_saisi, 
                           item_selectionne=item_selectionne, 
                           promo_cochee=promo_cochee)

if __name__ == '__main__':
    app.run(debug=True)
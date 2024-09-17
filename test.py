import pandas as pd

# Supposons que df soit votre DataFrame après moyennage
# Assurez-vous que la colonne de date est au format datetime
if df['horodatage'].dtype == 'object':  # Si la colonne est au format chaîne
    df['horodatage'] = pd.to_datetime(df['horodatage'], format='%Y_%m_%d_%H_%M_%S')

# Créez une colonne de date si elle n'existe pas
if 'date' not in df.columns:
    df['date'] = df['horodatage'].dt.strftime('%Y-%m-%d')

# Vérifiez les premiers enregistrements pour confirmer le format
print(df[['horodatage', 'date']].head())

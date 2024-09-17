import os
import pandas as pd
import re
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

# Choisir 'browser' comme mode de rendu par défaut
pio.renderers.default = 'browser'

# Lister les fichiers TXT dans le répertoire courant
txt_files = [f for f in os.listdir() if f.endswith('.txt')]

# Si aucun fichier TXT n'est trouvé, afficher un message d'erreur
if not txt_files:
    print("Aucun fichier TXT trouvé dans le répertoire actuel.")
    exit()

# Afficher les fichiers disponibles et demander à l'utilisateur d'en choisir un
print("Fichiers TXT disponibles :")
for i, file in enumerate(txt_files, 1):
    print(f"{i}. {file}")

choice = int(input("Sélectionnez un fichier par son numéro : ")) - 1
file_path = txt_files[choice]

# Extraire le nom de base du fichier sans l'extension
base_name = os.path.splitext(file_path)[0]

# Générer les noms de fichiers de sortie
csv_file_path = f"{base_name}.csv"
averaged_csv_file_path = f"{base_name}_averaged.csv"

# Ouvrir le fichier sélectionné et le convertir en CSV
with open(file_path, 'r') as file:
    lines = [line.strip().replace(';', ',') for line in file if line.strip() and not line.startswith('#')]

# Retirer les lignes qui correspondent au pattern "XX_XX_XX.CSV"
pattern = re.compile(r'^\d{2}_\d{2}_\d{2}\.CSV$')
lines = [line for line in lines if not pattern.match(line)]

# Déterminer le nombre attendu de champs à partir de la première ligne valide
expected_field_count = len(lines[0].split(','))

# Regex pour correspondre au bon format de timestamp
timestamp_pattern = re.compile(r'^\d{4}_\d{1,2}_\d{1,2}_\d{1,2}_\d{1,2}_\d{1,2}$')

# Traiter les lignes : remplacer les champs vides par 0 et filtrer les lignes avec un mauvais nombre de champs ou des timestamps incorrects
i = 0
j = 0
invalid_timestamp_count = 0
processed_lines = []
for line in lines:
    i += 1
    fields = line.split(',')
    if len(fields) == expected_field_count and timestamp_pattern.match(fields[0]):
        fields = ['0' if field == '' else field for field in fields]
        processed_lines.append(','.join(fields))
    else:
        if not timestamp_pattern.match(fields[0]):
            print(f"Ligne {i} a un timestamp invalide : {fields[0]}")
            invalid_timestamp_count += 1
        else:
            print(f"Ligne {i} a un nombre incorrect de champs : {len(fields)}")
        j += 1

print(f"{file_path}")
print(f"Lignes totales : {i}, Lignes incorrectes : {j}, Timestamps invalides : {invalid_timestamp_count}")

# Créer un fichier txt si il n'existe pas nommée 'resultats.txt' et y ajouter les informations de traitement
if not os.path.exists('resultats.txt'):
    with open('resultats.txt', 'w') as f:
        f.write(f"{file_path}\n")
        f.write(f"Lignes totales : {i}, Lignes incorrectes : {j}, Timestamps invalides : {invalid_timestamp_count}\n")
else:
    with open('resultats.txt', 'a') as f:
        f.write(f"{file_path}\n")
        f.write(f"Lignes totales : {i}, Lignes incorrectes : {j}, Timestamps invalides : {invalid_timestamp_count}\n")


# Ajouter la ligne d'en-tête en haut
header = "horodatage,PM1.0(ug/m3),PM2.5(ug/m3),PM10(ug/m3),N0.3(#/cm3),N0.5(#/cm3),N1(#/cm3),N2.5(#/cm3),N5(#/cm3),N10(#/cm3),T_DPS310(C),P_DPS310(Pa),H_HDC1080(%),battery level,T_AM2320_EXT(C),H_AM2320_EXT(%),Latitude,Longitude,Altitude,vitesse(km/h),nb de satellites"
processed_lines.insert(0, header)

# Écrire les données nettoyées dans le fichier CSV
with open(csv_file_path, 'w') as csv_file:
    csv_file.write('\n'.join(processed_lines))

# Define the data types for each column
dtype_dict = {
    'horodatage': 'str',
    'PM1.0(ug/m3)': 'float64',
    'PM2.5(ug/m3)': 'float64',
    'PM10(ug/m3)': 'float64',
    'N0.3(#/cm3)': 'float64',
    'N0.5(#/cm3)': 'float64',
    'N1(#/cm3)': 'float64',
    'N2.5(#/cm3)': 'float64',
    'N5(#/cm3)': 'float64',
    'N10(#/cm3)': 'float64',
    'T_DPS310(C)': 'float64',
    'P_DPS310(Pa)': 'float64',
    'H_HDC1080(%)': 'float64',
    'battery level': 'float64',
    'T_AM2320_EXT(C)': 'float64',
    'H_AM2320_EXT(%)': 'float64',
    'Latitude': 'float64',
    'Longitude': 'float64',
    'Altitude': 'float64',
    'vitesse(km/h)': 'float64',
    'nb de satellites': 'float64'
}

# Function to fix inconsistent timestamps (e.g., missing leading zero in seconds)
def fix_timestamp_format(timestamp):
    # Match a timestamp with a single-digit second and add a leading zero
    timestamp_fixed = re.sub(r'_(\d{1})(?=\s|,|$)', r'_0\1', timestamp)
    return timestamp_fixed

# List to keep track of invalid timestamps
invalid_timestamps = []

# Function to clean and check timestamps
def clean_and_check_timestamp(row, line_number):
    try:
        # First, try to fix the timestamp format
        row['horodatage'] = fix_timestamp_format(row['horodatage'])
        # Now try to convert to datetime, coercing errors
        row['horodatage'] = pd.to_datetime(row['horodatage'], format='%Y_%m_%d_%H_%M_%S', errors='raise')
        return row
    except Exception:
        # If timestamp is invalid, store the line number and timestamp value
        invalid_timestamps.append((line_number, row['horodatage']))
        return None  # Return None to skip this row later

# Read the CSV file with specified data types and error handling
df = pd.read_csv(
    csv_file_path,
    sep=',',
    dtype=str,  # Read all columns as strings initially
    on_bad_lines='skip'  # Skip bad lines
)

# Process each row and validate timestamps
cleaned_rows = []
for idx, row in df.iterrows():
    cleaned_row = clean_and_check_timestamp(row, idx)
    if cleaned_row is not None:
        cleaned_rows.append(cleaned_row)

# Create a new DataFrame from valid rows
df_cleaned = pd.DataFrame(cleaned_rows)

# Drop any rows with NaN in 'horodatage' (invalid timestamps will already be excluded)
df_cleaned = df_cleaned.dropna(subset=['horodatage'])

# Set 'horodatage' as the index of the DataFrame
df_cleaned.set_index('horodatage', inplace=True)

# Save the cleaned DataFrame to a new CSV file
df_cleaned.to_csv(csv_file_path, sep=',')

# Display the invalid timestamps and the number of total invalid timestamps
print(f"Total invalid timestamps: {len(invalid_timestamps)}")
if invalid_timestamps:
    print("Invalid timestamps (line number, timestamp):")
    for line_num, ts in invalid_timestamps:
        print(f"Ligne {line_num}: {ts}")

print(f"Total lignes traitées: {len(df)}")
print(f"Lignes valides: {len(df_cleaned)}")

# Ajouter une fonction pour moyenner toutes les colonnes en fonction de l'intervalle de temps choisi par l'utilisateur en secondes
# Ajouter une fonction pour moyenner toutes les colonnes en fonction de l'intervalle de temps choisi par l'utilisateur en secondes
def average_data(df, interval):
    # Convertir toutes les colonnes sauf 'horodatage' en données numériques
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Resample the data and calculate the mean for numeric columns only
    df_avg = df.resample(f'{interval}s').mean()

    # Drop rows with NaN values after resampling
    df_avg = df_avg.dropna()

    return df_avg

# Demander à l'utilisateur s'il veut moyenner les données
average_choice = input("Voulez-vous moyenner les données ? (Y/N) : ").upper()

if average_choice == 'Y':
    # Demander à l'utilisateur l'intervalle de temps pour moyenner les données en secondes
    interval = int(input("Entrez l'intervalle de temps pour moyenner les données en secondes : "))
    averaged_csv_file_path = f"{base_name}_averaged_{interval}sec.csv"
    df_avg = average_data(df_cleaned, interval)
    df_avg.to_csv(averaged_csv_file_path, sep=',')
    print(f"Les données ont été moyennées et enregistrées dans {averaged_csv_file_path}")
else:
    print("Les données n'ont pas été moyennées")

def insert_gaps(df, max_gap='5min'):
    # Convertir la colonne 'horodatage' en datetime si ce n'est pas déjà fait
    if 'horodatage' in df.columns:
        df['horodatage'] = pd.to_datetime(df['horodatage'])
        df.set_index('horodatage', inplace=True)

    # Calculer la différence de temps entre les points consécutifs
    df['time_diff'] = df.index.to_series().diff().shift(-1)

    # Insérer des valeurs NaN où l'écart de temps dépasse la valeur max_gap
    df_with_gaps = df.copy()
    df_with_gaps.loc[df['time_diff'] > pd.Timedelta(max_gap)] = None

    df_with_gaps = df_with_gaps.drop(columns=['time_diff'])
    return df_with_gaps

def convert_to_numeric(df, columns):
    for col in columns:
        # Convert the column to numeric, coerce errors to NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where any of the specified columns have NaN values
    df = df.dropna(subset=columns)
    return df

def normalize_series(series):
    return (series - series.min()) / (series.max() - series.min())

def convert_and_normalize(df, columns):
    df = convert_to_numeric(df, columns)
    # for col in columns:
    #     df[col] = normalize_series(df[col])
    return df

def plot_data(df):
    # Make sure data is sorted by horodatage before plotting
    df = df.sort_index()

    # Insert gaps in the data where time differences exceed a certain limit
    df = insert_gaps(df, max_gap='5min')

    # numerical columns
    numeric_columns = ['PM1.0(ug/m3)', 'PM2.5(ug/m3)', 'PM10(ug/m3)', 'N0.3(#/cm3)', 'N0.5(#/cm3)', 'N1(#/cm3)', 'N2.5(#/cm3)', 'N5(#/cm3)', 'N10(#/cm3)', 'T_DPS310(C)', 'P_DPS310(Pa)', 'H_HDC1080(%)', 'battery level', 'T_AM2320_EXT(C)', 'H_AM2320_EXT(%)']

    # Convert necessary columns to numeric types
    df = convert_and_normalize(df, numeric_columns)

    # Normalize PM data to unify the axis scales
    df['PM1.0(ug/m3)_normalized'] = normalize_series(df['PM1.0(ug/m3)'])
    df['PM2.5(ug/m3)_normalized'] = normalize_series(df['PM2.5(ug/m3)'])
    df['PM10(ug/m3)_normalized'] = normalize_series(df['PM10(ug/m3)'])


    # PM values plot
    fig_pm = go.Figure()
    fig_pm.add_trace(go.Scatter(x=df.index, y=df['PM1.0(ug/m3)'], mode='lines', name='PM1.0(ug/m3)', connectgaps=False))
    fig_pm.add_trace(go.Scatter(x=df.index, y=df['PM2.5(ug/m3)'], mode='lines', name='PM2.5(ug/m3)', connectgaps=False))
    fig_pm.add_trace(go.Scatter(x=df.index, y=df['PM10(ug/m3)'], mode='lines', name='PM10(ug/m3)', connectgaps=False))
    fig_pm.update_layout(
        title=f'Données PM - {file_path}',
        xaxis_title='Temps',
        yaxis_title='Concentration (ug/m3)',
        hovermode='x unified',
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=1, label="1j", step="day", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # N values plot
    fig_n = go.Figure()
    fig_n.add_trace(go.Scatter(x=df.index, y=df['N0.3(#/cm3)'], mode='lines', name='N0.3(#/cm3)', connectgaps=False))
    fig_n.add_trace(go.Scatter(x=df.index, y=df['N0.5(#/cm3)'], mode='lines', name='N0.5(#/cm3)', connectgaps=False))
    fig_n.add_trace(go.Scatter(x=df.index, y=df['N1(#/cm3)'], mode='lines', name='N1(#/cm3)', connectgaps=False))
    fig_n.add_trace(go.Scatter(x=df.index, y=df['N2.5(#/cm3)'], mode='lines', name='N2.5(#/cm3)', connectgaps=False))
    fig_n.add_trace(go.Scatter(x=df.index, y=df['N5(#/cm3)'], mode='lines', name='N5(#/cm3)', connectgaps=False))
    fig_n.add_trace(go.Scatter(x=df.index, y=df['N10(#/cm3)'], mode='lines', name='N10(#/cm3)', connectgaps=False))
    fig_n.update_layout(
        title=f'Données N - {file_path}',
        xaxis_title='Temps',
        yaxis_title='Nombre de particules (#/cm3)',
        hovermode='x unified',
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=1, label="1j", step="day", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # Temperature plot
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=df.index, y=df['T_DPS310(C)'], mode='lines', name='T_DPS310(C)', connectgaps=False))
    fig_temp.add_trace(go.Scatter(x=df.index, y=df['T_AM2320_EXT(C)'], mode='lines', name='T_AM2320_EXT(C)', connectgaps=False))
    fig_temp.update_layout(
        title=f'Données de température - {file_path}',
        xaxis_title='Temps',
        yaxis_title='Température (°C)',
        hovermode='x unified',
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=1, label="1j", step="day", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # Humidity plot
    fig_hum = go.Figure()
    fig_hum.add_trace(go.Scatter(x=df.index, y=df['H_HDC1080(%)'], mode='lines', name='H_HDC1080(%)', connectgaps=False))
    fig_hum.add_trace(go.Scatter(x=df.index, y=df['H_AM2320_EXT(%)'], mode='lines', name='H_AM2320_EXT(%)', connectgaps=False))
    fig_hum.update_layout(
        title=f'Données d\'humidité - {file_path}',
        xaxis_title='Temps',
        yaxis_title='Humidité (%)',
        hovermode='x unified',
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=1, label="1j", step="day", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # Pressure plot
    fig_press = go.Figure()
    fig_press.add_trace(go.Scatter(x=df.index, y=df['P_DPS310(Pa)'], mode='lines', name='P_DPS310(Pa)', connectgaps=False))
    fig_press.update_layout(
        title=f'Données de pression - {file_path}',
        xaxis_title='Temps',
        yaxis_title='Pression (Pa)',
        hovermode='x unified',
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=1, label="1j", step="day", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    fig_batt = go.Figure()
    fig_batt.add_trace(go.Scatter(x=df.index, y=df['battery level'], mode='lines', name='battery level', connectgaps=False))
    fig_batt.update_layout(
        title=f'Données de batterie - {file_path}',
        xaxis_title='Temps',
        yaxis_title='Niveau de batterie (%)',
        hovermode='x unified',
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=1, label="1j", step="day", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # Afficher les figures
    fig_pm.show()
    fig_n.show()
    fig_temp.show()
    fig_hum.show()
    fig_press.show()
    fig_batt.show()


def plot_map(df):
    # Convert necessary columns to numeric types
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df['Altitude'] = pd.to_numeric(df['Altitude'], errors='coerce')
    df['vitesse(km/h)'] = pd.to_numeric(df['vitesse(km/h)'], errors='coerce')
    df['nb de satellites'] = pd.to_numeric(df['nb de satellites'], errors='coerce')

    # Retirer les lignes où Latitude et Longitude sont nulles ou égales à 0
    df = df.dropna(subset=['Latitude', 'Longitude'])
    df = df[(df['Latitude'] != 0) & (df['Longitude'] != 0)]

    if df.empty:
        print("Aucune donnée valide pour afficher sur la carte.")
        return

    # Créer une carte avec les données GPS
    fig = px.scatter_mapbox(
        df,
        lat='Latitude',
        lon='Longitude',
        color='vitesse(km/h)',
        size='nb de satellites',
        hover_name='Altitude',
        hover_data={'vitesse(km/h)': True, 'Altitude': True, 'nb de satellites': True},
        zoom=10,
        mapbox_style="open-street-map",
        title="Trajectoire et Données GPS"
    )

    fig.show()


# Ask if the user wants to plot the data
plot_choice = input("Voulez-vous tracer les données ? (Y/N) : ").upper()

if plot_choice == 'Y':
    plot_data(df_cleaned)
else:
    print("Les données n'ont pas été tracées")

# Ask if the user wants to display the data on a map
map_choice = input("Voulez-vous afficher les données sur une carte ? (Y/N) : ").upper()

if map_choice == 'Y':
    plot_map(df_cleaned)
else:
    print("Les données n'ont pas été affichées sur la carte.")

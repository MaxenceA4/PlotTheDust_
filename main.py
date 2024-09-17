import pandas as pd
import plotly.graph_objects as go
from scipy.stats import linregress


# Pour lancer le programme, exécutez la commande suivante dans le terminal:
# python main.py
# Assurez-vous d'avoir installé les bibliothèques nécessaires en exécutant:
# pip install pandas plotly scipy
# Assurez-vous d'avoir le fichier data.csv dans le même répertoire que ce script
# Fonction pour moyennage des données
def average_data(df, window_size):
    df = df.copy()
    df.set_index('horodatage', inplace=True)
    df.index = pd.to_datetime(df.index, format='%Y_%m_%d_%H_%M_%S')

    # Sélectionner uniquement les colonnes numériques pour le moyennage
    numeric_cols = df.select_dtypes(include=['number']).columns

    df_resampled = df[numeric_cols].resample(f'{window_size}s').mean()
    df_resampled.index = df_resampled.index.strftime('%Y_%m_%d_%H_%M_%S')
    df_resampled.reset_index(inplace=True)
    return df_resampled


# Lire les données à partir du fichier CSV
file_path = 'data.csv'
df = pd.read_csv(file_path, delimiter=';')

# Convertir la colonne horodatage en datetime et extraire la date
df['horodatage'] = pd.to_datetime(df['horodatage'], format='%Y_%m_%d_%H_%M_%S')
df['date'] = df['horodatage'].dt.strftime('%Y-%m-%d')

# Demander si l'utilisateur veut moyenner les résultats
average_choice = input("Voulez-vous moyenner les résultats ? (O/N) : ").strip().upper()

if average_choice == 'O':
    window_size = int(input("Par paquet de combien de secondes voulez-vous moyenner les données ? : "))
    df = average_data(df, window_size)
    avg_file_path = 'data_averaged.csv'
    df.to_csv(avg_file_path, index=False, sep=';')
    print(f"Données moyennées enregistrées dans {avg_file_path}")

# Demander à l'utilisateur ce qu'il veut faire
choice = input(
    "Appuyez sur 'D' pour des graphiques jour par jour, 'A' pour un graphique global ou 'C' pour calibration: ").strip().upper()


def plot_calibration(daily_data, x_col, y_col, title):
    # Régression linéaire
    slope, intercept, r_value, p_value, std_err = linregress(daily_data[x_col], daily_data[y_col])
    r_squared = r_value ** 2

    # Tracer les données et la ligne de régression
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=daily_data[x_col], y=daily_data[y_col], mode='markers', name='Données'))
    fig.add_trace(go.Scatter(x=daily_data[x_col], y=slope * daily_data[x_col] + intercept, mode='lines',
                             name='Régression linéaire'))

    # Annotation pour l'équation et R^2
    annotation_text = f"Équation: y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.2f}"

    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
        annotations=[dict(
            x=0.05,
            y=0.95,
            xref='paper',
            yref='paper',
            text=annotation_text,
            showarrow=False,
            align='left',
            font=dict(size=12, color="black"),
            bgcolor="white",
            bordercolor="black"
        )],
        hovermode='closest'
    )

    fig.show()


# Si des données moyennées ont été générées, les utiliser
if average_choice == 'O':
    df = pd.read_csv(avg_file_path, delimiter=';')
    # Convertir à nouveau la colonne horodatage en datetime
    df['horodatage'] = pd.to_datetime(df['horodatage'], format='%Y_%m_%d_%H_%M_%S')
    df['date'] = df['horodatage'].dt.strftime('%Y-%m-%d')

if choice == 'D':
    # Créer des graphiques pour chaque jour
    unique_dates = df['date'].unique()

    for date in unique_dates:
        daily_data = df[df['date'] == date]

        # Graphique des PM
        fig_pm = go.Figure()
        fig_pm.add_trace(
            go.Scatter(x=daily_data['horodatage'], y=daily_data['PM1.0(ug/m3)'], mode='lines', name='PM1.0(ug/m3)'))
        fig_pm.add_trace(
            go.Scatter(x=daily_data['horodatage'], y=daily_data['PM2.5(ug/m3)'], mode='lines', name='PM2.5(ug/m3)'))
        fig_pm.add_trace(
            go.Scatter(x=daily_data['horodatage'], y=daily_data['PM10(ug/m3)'], mode='lines', name='PM10(ug/m3)'))
        fig_pm.update_layout(title=f'Particules PM - {date}', xaxis_title='Temps', yaxis_title='Concentration (ug/m3)',
                             hovermode='x unified')

        # Graphique des températures
        fig_temp = go.Figure()
        fig_temp.add_trace(
            go.Scatter(x=daily_data['horodatage'], y=daily_data['T_DPS310(C)'], mode='lines', name='T_DPS310(C)'))
        fig_temp.add_trace(
            go.Scatter(x=daily_data['horodatage'], y=daily_data['T_AM2320(C)'], mode='lines', name='T_AM2320(C)'))
        fig_temp.update_layout(title=f'Températures - {date}', xaxis_title='Temps', yaxis_title='Température (°C)',
                               hovermode='x unified')

        # Graphique de l'humidité
        fig_hum = go.Figure()
        fig_hum.add_trace(
            go.Scatter(x=daily_data['horodatage'], y=daily_data['H_HDC1080(%)'], mode='lines', name='H_HDC1080(%)'))
        fig_hum.add_trace(
            go.Scatter(x=daily_data['horodatage'], y=daily_data['H_AM2320(%)'], mode='lines', name='H_AM2320(%)'))
        fig_hum.update_layout(title=f'Humidité - {date}', xaxis_title='Temps', yaxis_title='Humidité (%)',
                              hovermode='x unified')

        # Afficher les graphiques
        fig_pm.show()
        fig_temp.show()
        fig_hum.show()

elif choice == 'A':
    # Graphique global des PM
    fig_pm = go.Figure()
    fig_pm.add_trace(go.Scatter(x=df['horodatage'], y=df['PM1.0(ug/m3)'], mode='lines', name='PM1.0(ug/m3)'))
    fig_pm.add_trace(go.Scatter(x=df['horodatage'], y=df['PM2.5(ug/m3)'], mode='lines', name='PM2.5(ug/m3)'))
    fig_pm.add_trace(go.Scatter(x=df['horodatage'], y=df['PM10(ug/m3)'], mode='lines', name='PM10(ug/m3)'))
    fig_pm.update_layout(title='Particules PM - Global', xaxis_title='Temps', yaxis_title='Concentration (ug/m3)',
                         hovermode='x unified')

    # Graphique global des températures
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=df['horodatage'], y=df['T_DPS310(C)'], mode='lines', name='T_DPS310(C)'))
    fig_temp.add_trace(go.Scatter(x=df['horodatage'], y=df['T_AM2320(C)'], mode='lines', name='T_AM2320(C)'))
    fig_temp.update_layout(title='Températures - Global', xaxis_title='Temps', yaxis_title='Température (°C)',
                           hovermode='x unified')

    # Graphique global de l'humidité
    fig_hum = go.Figure()
    fig_hum.add_trace(go.Scatter(x=df['horodatage'], y=df['H_HDC1080(%)'], mode='lines', name='H_HDC1080(%)'))
    fig_hum.add_trace(go.Scatter(x=df['horodatage'], y=df['H_AM2320(%)'], mode='lines', name='H_AM2320(%)'))
    fig_hum.update_layout(title='Humidité - Global', xaxis_title='Temps', yaxis_title='Humidité (%)',
                          hovermode='x unified')

    # Afficher les graphiques
    fig_pm.show()
    fig_temp.show()
    fig_hum.show()

elif choice == 'C':
    # Demander pour la calibration
    calib_choice = input(
        "Appuyez sur 'D' pour la calibration jour par jour ou 'A' pour la calibration globale : ").strip().upper()

    if calib_choice == 'D':
        unique_dates = df['date'].unique()
        for date in unique_dates:
            daily_data = df[df['date'] == date]

            # Calibration des températures
            plot_calibration(daily_data, 'T_DPS310(C)', 'T_AM2320(C)', f'Calibration Températures - {date}')

            # Calibration de l'humidité
            plot_calibration(daily_data, 'H_HDC1080(%)', 'H_AM2320(%)', f'Calibration Humidité - {date}')

    elif calib_choice == 'A':
        # Calibration globale des températures
        plot_calibration(df, 'T_DPS310(C)', 'T_AM2320(C)', 'Calibration Températures - Global')

        # Calibration globale de l'humidité
        plot_calibration(df, 'H_HDC1080(%)', 'H_AM2320(%)', 'Calibration Humidité - Global')

    else:
        print("Choix invalide. Veuillez appuyer sur 'D' ou 'A'.")

else:
    print("Choix invalide. Veuillez appuyer sur 'D', 'A', ou 'C'.")

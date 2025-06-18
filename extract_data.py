import requests
import pandas as pd
import os

import pandas as pd
from datetime import datetime


# # Cria pasta se não existir
# os.makedirs('db', exist_ok=True)

# # Requisição à API
# url = 'http://136.248.110.225:5000/api/dados'
# response = requests.get(url)

# dados = response.json()
# Salva dados brutos
arquivo_bruto = 'db/dados_temperatura.csv'

def process_and_group_data(file_path):
    # Processa e agrupa por hora
    df = pd.read_csv(file_path)

    df['temperatura'] = pd.to_numeric(df['temperatura'], errors='coerce')
    df['Datetime'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['temperatura', 'Datetime'])

    df.set_index('Datetime', inplace=True)

    df_hourly = df[['temperatura']].resample('h').mean().reset_index()

    # Formata timestamp final
    df_hourly['timestamp'] = df_hourly['Datetime'].dt.strftime('%Y-%m-%d %H:00:00')
    df_hourly[['timestamp', 'temperatura']].to_csv('db/dados_temperatura_por_hora.csv', index=False)

    print('Processamento concluído. CSVs salvos na pasta db.')

def get_current_temperature(file_path):
    df = pd.read_csv(file_path)
    df['Datetime'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['Datetime'])
    df.set_index('Datetime', inplace=True)
    
    # Obtém a temperatura mais recente
    current_temp = df['temperatura'].iloc[-1]
    return current_temp
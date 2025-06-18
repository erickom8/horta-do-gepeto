import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def prepare_data():
    """Prepara os dados de temperatura para treinamento do modelo.

    Esta função lê o arquivo CSV contendo os dados históricos de temperatura,
    processa as datas e cria as características necessárias para o modelo
    de previsão de temperatura.

    Returns
    -------
    pandas.DataFrame
        DataFrame contendo os dados processados com as seguintes colunas:
        - Datetime: Data e hora da medição
        - hour: Hora do dia (0-23)
        - day_of_week: Dia da semana (0-6)
        - month: Mês (1-12)
        - temperatura: Temperatura registrada
        - next_hour_temp: Temperatura da próxima hora (variável alvo)
    """
    # Alterar para o arquivo CSV contendo apenas os dados de temperatura por tempo
    df = pd.read_csv('db/dados_temperatura.csv')
    
    df['Datetime'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('Datetime')
    
    # Colunas para medição 
    df['hour'] = df['Datetime'].dt.hour
    df['day_of_week'] = df['Datetime'].dt.dayofweek
    df['month'] = df['Datetime'].dt.month
    
    # Criando variável alvo (temperatura da próxima hora)
    df['next_hour_temp'] = df['temperatura'].shift(-1)
    df = df.dropna() # Removendo valores nulos

    # Obtendo a última temperatura e data/hora registrada
    ultima_temperatura = df['temperatura'].iloc[-1]
    ultima_data_hora = df['Datetime'].iloc[-1]

    return df, ultima_temperatura, ultima_data_hora

def train_model():
    """Treina o modelo de regressão linear para previsão de temperatura.

    Esta função prepara os dados, treina um modelo de regressão linear
    e avalia seu desempenho usando métricas R².

    Returns
    -------
    sklearn.linear_model.LinearRegression
        Modelo treinado de regressão linear

    Notes
    -----
    O modelo é salvo em 'temperature_model.joblib' para uso futuro.
    """
    df, _, _ = prepare_data()   

    # Configurando parametros de source e target
    features = ['hour', 'day_of_week', 'month', 'temperatura']
    X = df[features]
    y = df['next_hour_temp']
    
    # Aplicando Treinamento para Regressão Linear
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    print('Calculando performance do modelo...')

    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"Model R² score on training data: {train_score:.3f}")
    print(f"Model R² score on test data: {test_score:.3f}")
    
    # Salvando modelo
    joblib.dump(model, 'temperature_model.joblib')
    
    return model

def predict_next_hour(current_temp, current_time):
    """Faz a previsão da temperatura para a próxima hora.

    Parameters
    ----------
    current_temp : float
        Temperatura atual em graus Celsius
    current_time : datetime
        Data e hora atual

    Returns
    -------
    float
        Temperatura prevista para a próxima hora em graus Celsius
    """
    # Carregando o modelo
    model = joblib.load('temperature_model.joblib')
    
    # Dados de input
    hour = current_time.hour
    day_of_week = current_time.weekday()
    month = current_time.month
    
    # Criação da lista dos dados para previsão
    features = np.array([[hour, day_of_week, month, current_temp]])
    prediction = model.predict(features)[0]
    
    return prediction

if __name__ == "__main__":
    print("Training the model...")
    model = train_model()
    
    # Obtendo a última temperatura e data/hora registrada
    _, current_temp, current_time = prepare_data()
    
    next_hour_temp = predict_next_hour(current_temp, current_time)
    print(f"\nPrediction for next hour ({current_time + timedelta(hours=1)}):")
    print(f"Current temperature: {current_temp}°C")
    print(f"Predicted temperature: {next_hour_temp:.2f}°C")



###
# PARA AMANHÃ:
# Este código será automatizado para fazer requisições à API externa
# a cada hora para obter:
# - Temperatura atual real
# - Timestamp atual
# Preciso tambem alterar o arquivo que esta sendo consumido para treinamento do modelo
#
# Exemplo de implementação futura:
# def get_current_data_from_api():
#     response = requests.get('URL_DA_API')
#     data = response.json()
#     return data['temperature'], data['timestamp']
###
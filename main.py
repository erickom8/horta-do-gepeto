import os
import uvicorn
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
from predict import predict_next_hour
from extract_data import process_and_group_data, get_current_temperature
from datetime import timedelta, datetime
from db import create_table, store_temperature
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
app = FastAPI()

# Variável global para armazenar a temperatura
current_temperature = 0.0

# Configurações do MQTT
broker = os.getenv("MQTT_BROKER")
topic = os.getenv("MQTT_TOPIC")
fan_topic = os.getenv("FAN_TOPIC")
print(fan_topic)

create_table()

# Função para receber a mensagem MQTT e armazenar a temperatura
def on_message(client, userdata, message):
    global current_temperature
    print("Entrando na função on_message()")
    message = subscribe.simple(topic, hostname=broker)
    current_temperature = float(message.payload.decode("utf-8"))
    print(current_temperature)
    control_fan(current_temperature)
    store_temperature(current_temperature)

# Configuração do cliente MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect(broker)
client.subscribe(topic)
client.loop_start() 

# Modelo para a resposta da API
class TemperatureResponse(BaseModel):
    temperature: float

@app.get("/temperature", response_model=TemperatureResponse)
def get_temperature():
    # Atualiza a temperatura atual a partir do arquivo processado
    current_temperature = get_current_temperature('db/dados_temperatura.csv')
    return TemperatureResponse(temperature=current_temperature)


def control_fan(temperature):
    current_time = datetime.now()
    next_hour_temp = predict_next_hour(temperature, current_time)
    print(f"\nPrediction for next hour ({current_time + timedelta(hours=1)}):")
    print(f"Current temperature: {temperature}°C")
    print(f"Predicted temperature: {next_hour_temp:.2f}°C")
    
    if next_hour_temp > 25.0:
        # Liga a ventoinha
        client.publish(fan_topic, "1")
        print("Ventoinha ligada")
    else:
        # Desliga a ventoinha
        client.publish(fan_topic, "0")
        print("Ventoinha desligada")

if __name__ == "__main__":
    process_and_group_data('db/dados_temperatura.csv')
    uvicorn.run(app, host="0.0.0.0", port=5000)
import os
import uvicorn
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
from db import create_table, store_temperature
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
app = FastAPI()

# Variável global para armazenar a temperatura
current_temperature = 0.0

# Configurações do MQTT
broker = os.getenv("MQTT_BROKER")  # Substitua pelo endereço do seu broker MQTT
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
    return TemperatureResponse(temperature=current_temperature)

def control_fan(temperature):
    if temperature > 25.0:
        # Liga a ventoinha
        client.publish(fan_topic, "1")
        print("Ventoinha ligada")
    else:
        # Desliga a ventoinha
        client.publish(fan_topic, "0")
        print("Ventoinha desligada")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
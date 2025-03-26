#include <ESP8266WiFi.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <DHT.h>

// Configurações do broker MQTT
const char* BROKER_MQTT = "test.mosquitto.org";
int BROKER_PORT = 1883;

// Tópicos MQTT
const char* TOPICO_TEMPERATURA = "horta/fatec/temp3r4tura";
const char* TOPICO_UMIDADE = "horta/fatec/um1d4d3";
const char* TOPICO_VENTOINHA = "horta/fatec/v3nto1nha";

#define DHTPIN 4 // GPIO4 (D2)
#define DHTTYPE DHT11
#define VENTOINHA_PIN 0
DHT dht(DHTPIN, DHTTYPE);

// Configuração da ventoinha
#define VENTOINHA_PIN 0 // GPIO0 (D3)

// Objetos para Wi-Fi e MQTT
WiFiClient espClient;
PubSubClient mqttClient(espClient);
const char* ID_MQTT = "ESP8266_Sensor_01";
const int max_try = 5;

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(VENTOINHA_PIN, OUTPUT);
  digitalWrite(VENTOINHA_PIN, LOW); // Ventoinha desligada inicialmente

  Serial.println("Turn ON!!!");
  dht.begin();

  WiFiManager wifiManager;
  int tentativas = 0;
  WiFi.mode(WIFI_STA);
  while (WiFi.status() != WL_CONNECTED && tentativas < max_try) {
    Serial.print("Tentando conectar ao Wi-Fi...");
    Serial.println(tentativas + 1);
    WiFi.begin();
    delay(5000);
    tentativas++;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Falha ao conectar, iniciando portal de configuração...");
    wifiManager.autoConnect("ESP8266-Sensor");
  }

  Serial.println("Conectado ao Wi-Fi!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  mqttClient.setServer(BROKER_MQTT, BROKER_PORT);
  mqttClient.setCallback(callbackMQTT); // Ainda usamos callback para receber mensagens
}

void loop() {
  if (!mqttClient.connected()) {
    conectaMQTT();
  }
  mqttClient.loop(); // Isso garante que as mensagens MQTT sejam processadas

  float temperatura = dht.readTemperature();
  float umidade = dht.readHumidity();

  if (!isnan(temperatura)) {
    Serial.print("Temperatura: "); Serial.print(temperatura); Serial.println(" ºC");
    mqttClient.publish(TOPICO_TEMPERATURA, String(temperatura).c_str());
  }

  if (!isnan(umidade)) {
    Serial.print("Umidade: "); Serial.print(umidade); Serial.println(" %");
    mqttClient.publish(TOPICO_UMIDADE, String(umidade).c_str());
  }

  delay(1000);
}

void conectaMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Conectando ao broker MQTT...");
    if (mqttClient.connect(ID_MQTT)) {
      Serial.println("Conectado!");
      mqttClient.subscribe(TOPICO_VENTOINHA); // Inscreve no tópico da ventoinha
    } else {
      Serial.print("Falha, rc="); Serial.print(mqttClient.state());
      Serial.println(" Tentando novamente em 5 segundos...");
      delay(5000);
    }
  }
}

void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  // Verifica se é o tópico da ventoinha
  if (strcmp(topic, TOPICO_VENTOINHA) == 0) {
    String msg = "";
    // Converte o payload para String
    for (unsigned int i = 0; i < length; i++) {
      msg += (char)payload[i];
    }
    
    // Remove espaços em branco e caracteres especiais
    msg.trim();
    
    Serial.print("Mensagem recebida para ventoinha: ");
    Serial.println(msg);

    // Controle da ventoinha
    if (msg == "1") {
      digitalWrite(VENTOINHA_PIN, HIGH); // Liga a ventoinha
      Serial.println("Ventoinha LIGADA");
    } 
    else if (msg == "0") {
      digitalWrite(VENTOINHA_PIN, LOW); // Desliga a ventoinha
      Serial.println("Ventoinha DESLIGADA");
    }
    else {
      Serial.println("Comando inválido! Use 1 para ligar ou 0 para desligar");
    }
  }
}

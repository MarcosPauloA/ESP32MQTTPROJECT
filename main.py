"""
Controlar leds e visualizar condições de tempo via broker

Instruções de uso:

1. Vá para https://www.hivemq.com/demos/websocket-client/
2. Clique em "Connect"
3. Embaixo de "Subscriptions", clique em "Add New Topic Subscription"
4. No campo "Topic", digite "previsaoDoTempo" então clique em "Subscribe"
5. Agora comece a simulação e espere o console printar "Envie uma mensagem MQTT de acordo com as instruções no topo do código"
6. Agora para controlar os LEDS:
7. Embaixo de Public, embaixo de Topic escreva "leds"
8. No campo Message escreva [255, 0, 0] (ou qualquer tipo de valor RGB)
9. clique em "Publish"
10. Para controlar o led comum No campo Message escreva "LIGAR" ou "DESLIGAR" e clique em Publish
"""

from machine import Pin
from time import sleep 

ledComum = Pin(21,Pin.OUT)

import dht
sensor = dht.DHT22(Pin(15))

from neopixel import NeoPixel
import ujson
def mqtt_message(topic, msg): #Função responsável pelos recebimento de mensagens MQTT e controle dos leds
  pixels = NeoPixel(Pin(13), 16)
  pixels.fill((0, 0, 0))
  pixels.write()
  print("Chegando mensagem MQTT:", msg)
  mensagem =msg.decode("utf-8")
  if mensagem == "LIGAR":
    ledComum.value(1)
  elif mensagem == "DESLIGAR":
    ledComum.value(0)
  else:
    try:
      msg = ujson.loads(msg)
      pixels.fill((msg[0], msg[1], msg[2]))
      pixels.write()
    except Exception as e:
      print("Error:", e)


def previsaoDoTempo(medicaoAnterior):
  print("Medindo condições metereorológicas... ", end="")
  sensor.measure() 
  message = ujson.dumps({
    "temperatura": sensor.temperature(),
    "umidade": sensor.humidity(),
  })
  if message != medicaoAnterior:
    print("Atualizado!")
    print("Reportando ao MQTT topic {}: {}".format(MQTT_TOPIC, message))
    client.publish(MQTT_TOPIC, message)
    return message
  else:
    print("Sem mudança no clima")


print("Conectando ao WiFi...", end="")
import network
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("Wokwi-GUEST", "")
while not wifi.isconnected():
  sleep(0.25)
  print(".", end="")
print("Conectado!")


print("Conectando ao MQTT...")
# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-weather-demo"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "previsaoDoTempo"
from umqtt.simple import MQTTClient
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()
client.set_callback(mqtt_message)
client.subscribe("leds")
print("Conectado!")
sleep(1)

def limpaConsole():
  print("\033c", end='')

medicaoAnterior = ""
while True:
  limpaConsole()
  medicaoAnterior = previsaoDoTempo(medicaoAnterior)
  print("Envie uma mensagem MQTT de acordo com as instruções no topo do código")
  client.wait_msg()
  sleep(1)


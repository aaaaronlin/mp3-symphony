import paho.mqtt.client as paho
import time

session = "PPAL/ESP32/stuff/"
BROKER = "iot.eclipse.org"

print("Connecting to MQTT broker", BROKER, "...", end="")
mqtt = paho.Client()
mqtt.connect(BROKER, 1883)
time.sleep(0.5)
print("Connected!")

def send_MCU(data):
    message = "field1={}".format(data)
    mqtt.publish(session, payload=message, qos=0)
    print("Sent! Now playing on wind chimes...")

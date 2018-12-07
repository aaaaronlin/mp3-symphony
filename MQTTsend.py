import paho.mqtt.client as paho
import time

session = "MP3Symphony/midi"
BROKER = "broker.hivemq.com"

print("Connecting to MQTT broker", BROKER, "...", end="")
mqtt = paho.Client()
mqtt.connect(BROKER)
time.sleep(0.5)
mqtt.subscribe(session)
print("Connected!")

msg = ''

def on_message(client, userdata, message):
    global msg
    msg = str(message.payload.decode("utf-8"))

mqtt.on_message = on_message

def send_MCU(data):
    message = "{}".format(data)
    mqtt.publish(session, payload=message, qos=0)
    print("Sent! Now playing on wind chimes...")

def receive_MCU():
    mqtt.loop_start()
    time.sleep(5)
    mqtt.loop_stop()
    return msg
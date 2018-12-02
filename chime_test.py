from machine import Pin, Timer, ENC, PWM
from board import A1, A6, A7, A18, A19
from time import ticks_ms, sleep
from mqttclient import MQTTClient
import network

session = "MP3Symphony/midi"
BROKER = "iot.eclipse.org"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
mqtt = MQTTClient(BROKER)

def mqtt_callback(topic, msg):
    raw_midi = msg.decode('utf-8')
    real_midi = manage_midi(raw_midi)
    if real_midi != 0:
        play(real_midi)

mqtt.set_callback(mqtt_callback)
mqtt.subscribe(session)
mqtt.publish(session, "connected and waiting...")

# parsing data string format: (note_num, length(seconds)/ ex: 0,0/4,5.6/12,0.6...)
def manage_midi(raw_midi):
    try:
        a = raw_midi.split("/")
        list_midi = [i.split(",") for i in a]
        converted_midi = [[float(y) for y in x] for x in list_midi]
        count_midi = [[i[0] * 75, i[1]] for i in converted_midi]
        return count_midi
    except:
        return 0

# encoder setup
enc0_pinA = Pin(A6)
enc0_pinB = Pin(A7)
enc0 = ENC(0, enc0_pinA, enc0_pinB)
enc0.filter(1023)

# motor setup
p1 = Pin(A18, mode=Pin.OPEN_DRAIN)
p2 = Pin(A19, mode=Pin.OPEN_DRAIN)
m1 = PWM(p1, freq=50000, duty=0, timer=0)
m2 = PWM(p2, freq=50000, duty=0, timer=0)

# solenoid setup
s0 = Pin(A1, mode=Pin.OUT)
solenoid_constant = 100

# callable actions
def punch():
    global s0
    s0(1)
    t1 = ticks_ms() + solenoid_constant
    while ticks_ms() < t1:
        continue
    s0(0)

def m0_turn(turn):
    global enc0
    t0 = ticks_ms()
    if turn == 0:
        return 0
    if turn > 0:
        m1.duty(100)
        m2.duty(0)
    else:
        m1.duty(0)
        m2.duty(100)
    while abs(enc0.count()) < abs(turn):
        continue
    m1.duty(0)
    m2.duty(0)
    return (ticks_ms() - t0) / 1000


def m0_origin(note):
    m1.duty(0)
    m2.duty(100)
    while abs(enc0.count()) < note:
        continue
    m2.duty(0)
    enc0.clear()

def play(list):
    global enc0
    size = len(list)
    m0_turn(list[0][0])
    prev_note = list[0][0]
    for number0 in range(1, size-1):
        enc0.clear()
        note = list[number0][0]
        length = list[number0][1]
        if length > 0.5 or note != 0:
            turn = note - prev_note
            t0 = m0_turn(turn)
            punch()
            sleep(length - t0 - solenoid_constant/1000)
        else:
            sleep(length)
        prev_note = note
    m0_origin(list[size][0])

# MQTT timer

def readMSG(readMQTT):
    mqtt.check_msg()

readMQTT = Timer(2)

#readMQTT.init(period=5000, mode=readMQTT.PERIODIC, callback=readMSG)

def test():
    global enc0
    m1.duty(100)
    m2.duty(0)
    print(enc0.count())
    sleep(1)
    print(enc0.count())
    sleep(1)

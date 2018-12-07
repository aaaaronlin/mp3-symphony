from machine import Pin, Timer, ENC, PWM
from board import A1, A6, A7, A18, A19
from time import ticks_ms, sleep
from mqttclient import MQTTClient
import network

session = "MP3Symphony/midi"
BROKER = "broker.hivemq.com"
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
    global readMQTT
    try:
        a = raw_midi.split("/")
        list_midi = [i.split(",") for i in a]
        converted_midi = [[float(y) for y in x] for x in list_midi]
        count_midi = [[i[0], i[1]] for i in converted_midi]
        readMQTT.deinit()
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
duty = 90
brake_constant = 100
punch_constant = 10
turn_list = [0, 16, 47, 90, 141, 198, 261, 328, 398, 468, 539, 610]

# solenoid setup
s0 = Pin(A1, mode=Pin.OUT)

# callable actions
def punch():
    global s0
    s0(1)
    t1 = ticks_ms() + punch_constant
    while ticks_ms() < t1:
        continue
    s0(0)

def m0_turn(turn):
    global enc0
    if turn == 0:
        return 0
    if turn > 0:
        m1.duty(duty)
        m2.duty(0)
    else:
        m1.duty(0)
        m2.duty(duty)
    while abs(enc0.count()) < abs(turn):
        continue

def brake():
    t = ticks_ms() + brake_constant
    while ticks_ms() < t:
        m1.duty(100)
        m2.duty(100)
    m1.duty(0)
    m2.duty(0)

def play(list):
    global enc0, s0
    size = len(list)
    prev_note = 1
    for i in range(0, size-1):
        enc0.clear()
        note = list[i][0]
        length = list[i][1]
        if note != 0:
            path = get_best_path(note, prev_note, mode=2)
            ind = turn_list[abs(path)]
            print(ind)
            if path < 0:
                m0_turn(-ind)
            else:
                m0_turn(ind)
            brake()
            punch()
            sleep(length)
            prev_note = note
        else:
            sleep(length)
    m0_turn(get_best_path(1, prev_note, mode=1))
    brake()
    s0(0)
# MQTT timer
def readMSG(readMQTT):
    mqtt.check_msg()

readMQTT = Timer(2)

readMQTT.init(period=5000, mode=readMQTT.PERIODIC, callback=readMSG)

#modes: 1 for shortest path, 2 for half-rotation max (wires in the way)

def get_best_path(note, prev_note, mode):
    turn_comp = []
    if mode == 1:
        turn_comp.append(note - prev_note)
        turn_comp.append(note - prev_note + 12)
        turn_comp.append(note - prev_note - 12)
        turn_comp_abs = [abs(x) for x in turn_comp]
        dist = turn_comp_abs.index(min(turn_comp_abs))
    elif mode == 2:
        if prev_note > 6:
            if note <= 6:
                dist = note - prev_note + 12
            else:
                dist = note - prev_note
        else:
            if note <= 6:
                dist = note - prev_note
            else:
                dist = note - prev_note - 12
    return int(dist)

# others
s0(0)

def test(turn):
    global enc0
    enc0.clear()
    m0_turn(turn)
    brake()
    punch()
    print(enc0.count())

#if __name__ == "__main__":
#    msg = '0,0/1,1/2,1/3,1/4,1/5,1/6,1/7,1/8,1/9,1/10,1/11,1/0,0'
#    mqtt_callback('test', msg.encode())

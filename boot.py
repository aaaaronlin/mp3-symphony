# Establish Internet connection
from network import WLAN, STA_IF
from network import mDNS
import time

wlan = WLAN(STA_IF)
wlan.active(True)

wlan.connect('MotoG Boi', 'aarontest4', 5000)

while not wlan.isconnected():
    print("Waiting for wlan connection")
    time.sleep(1)

print("WiFi connected at", wlan.ifconfig()[0])

# Advertise as 'hostname', alternative to IP address
try:
    hostname = 'aaron&prom'
    mdns = mDNS(wlan)
    mdns.start(hostname, "MicroPython REPL")
    mdns.addService('_repl', '_tcp', 23, hostname)
    print("Advertised locally as {}.local".format(hostname))
except OSError:
    print("Failed starting mDNS server - already started?")
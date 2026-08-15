import network
import webrepl
import time

# WLAN Konfiguration
SSID = "DEIN_WLAN_NAME"
PASSWORD = "DEIN_WLAN_PASSWORT"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    print("Verbinde mit WLAN...")
    wlan.connect(SSID, PASSWORD)
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

if wlan.isconnected():
    print("WLAN verbunden! IP:", wlan.ifconfig()[0])
else:
    print("WLAN Verbindung fehlgeschlagen!")

# WebREPL starten (Passwort in webrepl_cfg.py konfiguriert)
webrepl.start()

# AZ-Touch MOD ESP32 MicroPython Driver & Test App

Ein vollständiger, optimierter und einsatzbereiter MicroPython-Treiber und Testprogramm für das **AZ-Delivery AZ-Touch MOD** (oder ArduiTouch) Gehäuse-Kit mit ESP32, 2.4" / 2.8" SPI TFT Display (**ILI9341**), resistivem Touchscreen (**XPT2046**), PWM-Hintergrundbeleuchtung und Piezo-Buzzer.

---

## ✨ Features

- **ILI9341 TFT Display (320x240 Querformat):** Schnelle SPI-Ansteuerung (20 MHz) mit sauberen Grafik-Primitiven (Rechtecke, Linien, Text, Buttons).
- **XPT2046 Touch-Controller mit dynamischer Taktumschaltung:**
  - Löst das bekannte Problem geteilter SPI-Busse: Der ESP32 schaltet bei Touch-Abfragen automatisch auf **1 MHz** herunter und für das Display wieder auf **20 MHz** hoch.
  - Hardware-Interrupt (`T_IRQ` auf GPIO 27) mit Entprellung und Multi-Sampling.
  - Vollständige Kalibrierung für Querformat ($320 \times 240$, korrekte X/Y- und Oben/Unten-Zuordnung).
- **PWM-Hintergrundbeleuchtung (GPIO 15):** Stufenlos dimmbar (100 %, 75 %, 50 %, 25 %, 10 %, Aus) mit korrekter invertierter Ansteuerung für den T1-Transistor.
- **Akustisches Feedback (Buzzer auf GPIO 21):** PWM-gesteuerter Piezo-Ton bei Tastendruck und Aktionen (via T2-Transistor).
- **OTA / WebREPL tauglich:** Kann komplett drahtlos über WLAN per WebREPL geflasht, verwaltet und ausgeführt werden.

---

## 📌 Pinbelegung (AZ-Touch MOD ESP32)

| Komponente | Signal | ESP32 GPIO | Beschreibung |
| :--- | :--- | :--- | :--- |
| **Display (ILI9341)** | `TFT_CS` | **GPIO 5** | Display Chip Select |
| | `TFT_DC` | **GPIO 4** | Data / Command |
| | `TFT_RST` | **GPIO 22** | Hardware Reset |
| | `LED` | **GPIO 15** | Hintergrundbeleuchtung (PWM via Transistor T1, Invertiert) |
| **Touch (XPT2046)** | `T_CS` | **GPIO 14** | Touch Controller Chip Select |
| | `T_IRQ` | **GPIO 27** | Touch Interrupt (Active LOW bei Berührung) |
| **Gemeinsamer SPI-Bus** | `SCK` | **GPIO 18** | SPI Taktleitung (VSPI SCK) |
| | `MOSI` | **GPIO 23** | SPI Daten zum Display/Touch (VSPI MOSI) |
| | `MISO` | **GPIO 19** | SPI Daten vom Touch (VSPI MISO) |
| **Beeper / Akustik** | `BEEPER` | **GPIO 21** | Piezo-Buzzer (PWM via Transistor T2) |

---

## 📂 Projektstruktur

```text
az-touch-esp32/
├── boot.py               # WLAN- & WebREPL-Initialisierung
├── main.py               # Autostart des Testprogramms
├── tft_test.py           # Hauptprogramm mit UI, Touch-Logik & Buzzer
├── drivers/
│   ├── ili9341.py        # MicroPython ILI9341 Display-Treiber
│   └── xpt2046.py        # MicroPython XPT2046 Touch-Treiber
├── tools/
│   ├── webrepl_cli.py    # CLI-Tool für drahtlose Dateiübertragung
│   └── esp_exec.py       # Skript zur Remote-Codeausführung via WebREPL
└── README.md
```

---

## 🚀 Installation & Schnellstart

### 1. Dateien auf den ESP32 übertragen

#### Über WebREPL (WLAN):
```bash
# Display- und Touch-Treiber hochladen
python3 tools/webrepl_cli.py -p <PASSWORT> drivers/ili9341.py <ESP_IP>:ili9341.py
python3 tools/webrepl_cli.py -p <PASSWORT> drivers/xpt2046.py <ESP_IP>:xpt2046.py

# Hauptprogramm & Autostart hochladen
python3 tools/webrepl_cli.py -p <PASSWORT> tft_test.py <ESP_IP>:tft_test.py
python3 tools/webrepl_cli.py -p <PASSWORT> main.py <ESP_IP>:main.py
```

#### Über USB / mpremote:
```bash
mpremote connect /dev/ttyUSB0 fs cp drivers/ili9341.py :ili9341.py
mpremote connect /dev/ttyUSB0 fs cp drivers/xpt2046.py :xpt2046.py
mpremote connect /dev/ttyUSB0 fs cp tft_test.py :tft_test.py
mpremote connect /dev/ttyUSB0 fs cp main.py :main.py
```

### 2. Starten
Nach einem Neustart (`machine.soft_reset()`) verbindet sich der ESP32 mit dem WLAN und startet die grafische Test-Applikation automatisch.

---

## 📱 Oberfläche & Bedienung

- **Statuszeile:** Zeigt WLAN-IP, freien RAM-Speicher und Live-Touch-Koordinaten $(X, Y)$.
- **Zeichenfläche:** Erlaubt das Zeichnen von Markierungen direkt mit dem Finger oder Stylus.
- **Buttons:**
  - **`[ BEEP ]`** – Erzeugt einen 3,8 kHz Testton auf dem Buzzer.
  - **`[ 50% ]`** – Schaltet die Display-Helligkeit in Stufen durch ($100\% \rightarrow 75\% \rightarrow 50\% \rightarrow 25\% \rightarrow 10\% \rightarrow 0\%$).
  - **`[ COLOR ]`** – Wechselt das Farbdesign der Kopfzeile.
  - **`[ CLEAR ]`** – Bereinigt die Zeichenfläche.

---

## 📄 Lizenz
MIT License. Freie Verwendung für private und kommerzielle Projekte.

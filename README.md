<p align="center">
  <b><a href="#-english">🇬🇧 English</a></b> &nbsp;•&nbsp; <b><a href="#-deutsch">🇩🇪 Deutsch</a></b>
</p>

---

<a name="-english"></a>
# AZ-Touch MOD ESP32 MicroPython Driver & Test App

A complete, optimized, and ready-to-use MicroPython driver and test application for the **AZ-Delivery AZ-Touch MOD** (or ArduiTouch) enclosure kit with ESP32, 2.4" / 2.8" SPI TFT Display (**ILI9341**), resistive touchscreen (**XPT2046**), PWM backlight, and piezo buzzer.

---

## ✨ Features

- **ILI9341 TFT Display (320x240 Landscape):** Fast SPI driver (20 MHz) with clean graphics primitives (rectangles, lines, text, buttons).
- **XPT2046 Touch Controller with Dynamic Bus Clock Switching:**
  - Solves the common shared-SPI-bus issue: ESP32 automatically down-clocks SPI to **1 MHz** during touch reading and restores **20 MHz** for display rendering.
  - Hardware interrupt (`T_IRQ` on GPIO 27) with debounce and multi-sampling.
  - Fully calibrated for landscape orientation ($320 \times 240$, correct X/Y and top/bottom mapping).
- **PWM Backlight Dimming (GPIO 15):** Stepless brightness control (100%, 75%, 50%, 25%, 10%, Off) with proper inverted logic for the T1 transistor.
- **Acoustic Feedback (Buzzer on GPIO 21):** PWM-driven piezo tone on touch events and button presses (via T2 transistor).
- **OTA / WebREPL Ready:** Fully wireless flashing, configuration, and execution over Wi-Fi via WebREPL.

---

## 📌 Pinout (AZ-Touch MOD ESP32)

| Component | Signal | ESP32 GPIO | Description |
| :--- | :--- | :--- | :--- |
| **Display (ILI9341)** | `TFT_CS` | **GPIO 5** | Display Chip Select |
| | `TFT_DC` | **GPIO 4** | Data / Command |
| | `TFT_RST` | **GPIO 22** | Hardware Reset |
| | `LED` | **GPIO 15** | Backlight (PWM via Transistor T1, Inverted) |
| **Touch (XPT2046)** | `T_CS` | **GPIO 14** | Touch Controller Chip Select |
| | `T_IRQ` | **GPIO 27** | Touch Interrupt (Active LOW on touch) |
| **Shared SPI Bus** | `SCK` | **GPIO 18** | SPI Clock (VSPI SCK) |
| | `MOSI` | **GPIO 23** | SPI Data to Display/Touch (VSPI MOSI) |
| | `MISO` | **GPIO 19** | SPI Data from Touch (VSPI MISO) |
| **Beeper / Audio** | `BEEPER` | **GPIO 21** | Piezo Buzzer (PWM via Transistor T2) |

---

## 📂 Project Structure

```text
az-touch-esp32/
├── boot.py               # Wi-Fi & WebREPL initialization
├── main.py               # Autostart wrapper for the test app
├── tft_test.py           # Main application with UI, touch logic & buzzer
├── drivers/
│   ├── ili9341.py        # MicroPython ILI9341 display driver
│   └── xpt2046.py        # MicroPython XPT2046 touch driver
├── tools/
│   ├── webrepl_cli.py    # CLI tool for wireless file transfer
│   └── esp_exec.py       # Script for remote code execution via WebREPL
└── README.md
```

---

## 🚀 Installation & Quick Start

### 1. Transfer Files to ESP32

#### Via WebREPL (Wi-Fi):
```bash
# Upload display and touch drivers
python3 tools/webrepl_cli.py -p <PASSWORD> drivers/ili9341.py <ESP_IP>:ili9341.py
python3 tools/webrepl_cli.py -p <PASSWORD> drivers/xpt2046.py <ESP_IP>:xpt2046.py

# Upload main test app & autostart script
python3 tools/webrepl_cli.py -p <PASSWORD> tft_test.py <ESP_IP>:tft_test.py
python3 tools/webrepl_cli.py -p <PASSWORD> main.py <ESP_IP>:main.py
```

#### Via USB / mpremote:
```bash
mpremote connect /dev/ttyUSB0 fs cp drivers/ili9341.py :ili9341.py
mpremote connect /dev/ttyUSB0 fs cp drivers/xpt2046.py :xpt2046.py
mpremote connect /dev/ttyUSB0 fs cp tft_test.py :tft_test.py
mpremote connect /dev/ttyUSB0 fs cp main.py :main.py
```

### 2. Run
After a soft reset (`machine.soft_reset()`), the ESP32 connects to Wi-Fi and automatically launches the graphical test suite.

---

## 📱 Interface & Controls

- **Status Bar:** Shows Wi-Fi IP address, free heap RAM, and live touch coordinates $(X, Y)$.
- **Canvas:** Allows drawing freehand strokes with finger or stylus.
- **Buttons:**
  - **`[ BEEP ]`** – Plays a 3.8 kHz confirmation tone on the buzzer.
  - **`[ 50% ]`** – Cycles through backlight levels ($100\% \rightarrow 75\% \rightarrow 50\% \rightarrow 25\% \rightarrow 10\% \rightarrow 0\%$).
  - **`[ COLOR ]`** – Cycles header color theme.
  - **`[ CLEAR ]`** – Clears the touch canvas.

---

## 📄 License
MIT License. Free for private and commercial use.

---
---

<a name="-deutsch"></a>
# 🇩🇪 Deutsche Beschreibung

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

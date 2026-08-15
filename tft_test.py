"""
AZ-Delivery AZ-Touch MOD Test Program for ESP32
Includes:
- Display: ILI9341 on SPI (320x240, CS=5, DC=4, RST=22, LED=15 PWM inverted)
- Touch: XPT2046 with dynamic SPI frequency switching (CS=14, IRQ=27)
- Landscape Axis Mapping (X & Y fully calibrated, Top/Bottom corrected)
- Beeper: Piezo buzzer on GPIO 21 (via T2)
"""

import time
import gc
import network
from machine import Pin, SPI, PWM
import ili9341
from ili9341 import color565

# Colors (RGB565)
BLACK    = color565(0, 0, 0)
NAVY     = color565(10, 25, 60)
BLUE     = color565(0, 120, 215)
CYAN     = color565(0, 220, 220)
GREEN    = color565(40, 200, 60)
YELLOW   = color565(255, 220, 0)
ORANGE   = color565(255, 140, 0)
RED      = color565(230, 40, 40)
WHITE    = color565(255, 255, 255)
GRAY     = color565(80, 80, 80)
DARKGRAY = color565(30, 30, 30)

class AZTouchApp:
    def __init__(self, initial_brightness=50):
        print("[AZ-Touch] Starting Hardware Setup...")

        # 1. Backlight (GPIO 15 PWM, active LOW / inverted logic via T1)
        self.brightness = initial_brightness
        self.brightness_levels = [100, 75, 50, 25, 10, 0]
        try:
            self.pwm_led = PWM(Pin(15), freq=1000)
            self.set_brightness(self.brightness)
        except Exception:
            self.pwm_led = None
            Pin(15, Pin.OUT, value=0)

        # 2. Buzzer (GPIO 21)
        self.buzzer_pin = Pin(21, Pin.OUT, value=0)

        # 3. Dedicated CS Pins
        self.tft_cs = Pin(5, Pin.OUT, value=1)
        self.touch_cs = Pin(14, Pin.OUT, value=1)

        # 4. Touch IRQ pin (GPIO 27, Active LOW on touch)
        self.irq = Pin(27, Pin.IN, Pin.PULL_UP)

        # 5. Shared SPI Bus (SCK=18, MOSI=23, MISO=19)
        self.spi = SPI(2, baudrate=20000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

        # 6. Display Init (320x240 Landscape, rotation=90)
        print("[AZ-Touch] Initializing ILI9341 Display...")
        self.display = ili9341.Display(
            self.spi,
            cs=self.tft_cs,
            dc=Pin(4),
            rst=Pin(22),
            width=320,
            height=240,
            rotation=90
        )

        # Buffer for touch SPI
        self.tx_buf = bytearray(3)
        self.rx_buf = bytearray(3)

        # Calibration for 320x240 Landscape
        self.raw_x_min = 280
        self.raw_x_max = 3850
        self.raw_y_min = 280
        self.raw_y_max = 3850

        # Network Info
        wlan = network.WLAN(network.STA_IF)
        self.ip = wlan.ifconfig()[0] if wlan.isconnected() else "Kein WLAN"

        # UI Theme
        self.color_idx = 0
        self.theme_colors = [BLUE, GREEN, ORANGE, RED, CYAN]

        # Buttons (x, y, w, h, id, label, color)
        self.buttons = [
            {"id": "BEEP",  "x": 10,  "y": 185, "w": 68, "h": 45, "label": "BEEP",  "bg": BLUE},
            {"id": "LIGHT", "x": 86,  "y": 185, "w": 68, "h": 45, "label": f"{self.brightness}%", "bg": GREEN},
            {"id": "COLOR", "x": 162, "y": 185, "w": 68, "h": 45, "label": "COLOR", "bg": ORANGE},
            {"id": "CLEAR", "x": 238, "y": 185, "w": 72, "h": 45, "label": "CLEAR", "bg": RED},
        ]

    def set_brightness(self, percent):
        """Set LCD backlight brightness (0 - 100%) with inverted PWM logic for T1."""
        self.brightness = max(0, min(100, percent))
        if self.pwm_led:
            # Inverted logic: 100% -> Duty 0, 0% -> Duty 1023
            duty_val = int(((100.0 - self.brightness) / 100.0) * 1023)
            self.pwm_led.duty(duty_val)
        print(f"[AZ-Touch] Backlight set to {self.brightness}% (Duty: {duty_val})")

    def cycle_brightness(self):
        curr_idx = self.brightness_levels.index(self.brightness) if self.brightness in self.brightness_levels else 0
        next_idx = (curr_idx + 1) % len(self.brightness_levels)
        self.set_brightness(self.brightness_levels[next_idx])
        for btn in self.buttons:
            if btn["id"] == "LIGHT":
                btn["label"] = f"{self.brightness}%"
                self.draw_button(btn)

    def beep(self, freq=3000, duration_ms=50):
        try:
            pwm = PWM(Pin(21), freq=freq, duty=512)
            time.sleep_ms(duration_ms)
            pwm.deinit()
            Pin(21, Pin.OUT, value=0)
        except Exception:
            pass

    def _read_xpt_raw(self, cmd):
        """Read a single channel from XPT2046 with clock switched to 1 MHz."""
        self.tx_buf[0] = cmd
        self.tx_buf[1] = 0x00
        self.tx_buf[2] = 0x00

        # Ensure Display is unselected
        self.tft_cs.value(1)

        # Set SPI clock to 1 MHz for XPT2046
        self.spi.init(baudrate=1000000)

        # Read 3 bytes via SPI
        self.touch_cs.value(0)
        self.spi.write_readinto(self.tx_buf, self.rx_buf)
        self.touch_cs.value(1)

        # Restore SPI clock to 20 MHz for Display
        self.spi.init(baudrate=20000000)

        # Standard 12-bit extraction (bits D11..D0)
        val = ((self.rx_buf[1] << 8) | self.rx_buf[2]) >> 3
        return val

    def get_touch_pos(self):
        """
        Poll touch and return (is_touched, screen_x, screen_y, raw_x, raw_y).
        Maps swapped Landscape axes with correct Top/Bottom orientation.
        """
        # Hardware IRQ on AZ-Touch goes LOW (0) when screen is pressed
        is_pressed = (self.irq.value() == 0)
        if not is_pressed:
            return False, 0, 0, 0, 0

        # Read samples
        samples_x = []
        samples_y = []
        for _ in range(3):
            rx = self._read_xpt_raw(0xD0)
            ry = self._read_xpt_raw(0x90)
            if 100 < rx < 4000 and 100 < ry < 4000:
                samples_x.append(rx)
                samples_y.append(ry)
            time.sleep_us(50)

        if not samples_x or not samples_y:
            rx = self._read_xpt_raw(0xD0)
            ry = self._read_xpt_raw(0x90)
            if rx < 100 or ry < 100:
                return True, 0, 0, rx, ry
            avg_x, avg_y = rx, ry
        else:
            avg_x = sum(samples_x) // len(samples_x)
            avg_y = sum(samples_y) // len(samples_y)

        # Map to 320x240 Landscape:
        # Screen X (0..319) mapped from Touch Y sensor (inverted)
        norm_x = (self.raw_y_max - avg_y) / (self.raw_y_max - self.raw_y_min)
        # Screen Y (0..239) mapped from Touch X sensor (inverted for correct Top/Bottom)
        norm_y = (self.raw_x_max - avg_x) / (self.raw_x_max - self.raw_x_min)

        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))

        sx = int(norm_x * 320)
        sy = int(norm_y * 240)

        sx = max(0, min(319, sx))
        sy = max(0, min(239, sy))

        return True, sx, sy, avg_x, avg_y

    def draw_button(self, btn, pressed=False):
        x, y, w, h = btn["x"], btn["y"], btn["w"], btn["h"]
        bg = WHITE if pressed else btn["bg"]
        fg = BLACK if pressed else WHITE
        self.display.fill_rectangle(x, y, w, h, bg)
        self.display.draw_rectangle(x, y, w, h, WHITE)
        self.display.draw_rectangle(x+1, y+1, w-2, h-2, DARKGRAY if not pressed else GRAY)
        lbl = btn["label"]
        tx = x + (w - len(lbl)*8) // 2
        ty = y + (h - 8) // 2
        self.display.draw_text8x8(tx, ty, lbl, fg, background=bg)

    def draw_canvas(self):
        self.display.fill_rectangle(10, 68, 300, 108, DARKGRAY)
        self.display.draw_rectangle(10, 68, 300, 108, GRAY)
        self.display.draw_text8x8(16, 75, "Touch & Zeichenflaeche:", CYAN, background=DARKGRAY)
        self.display.draw_text8x8(16, 92, "Auf das Display druecken!", WHITE, background=DARKGRAY)

    def draw_ui(self):
        self.display.clear(NAVY)
        # Header
        self.display.fill_rectangle(0, 0, 320, 28, self.theme_colors[self.color_idx])
        self.display.draw_text8x8(16, 10, "AZ-Touch MOD (ESP32 Test)", WHITE, background=self.theme_colors[self.color_idx])
        
        # System & Touch Info
        info_str = f"IP:{self.ip}  RAM:{gc.mem_free()//1024}kB"
        self.display.draw_text8x8(10, 35, info_str, YELLOW, background=NAVY)
        self.display.draw_text8x8(10, 48, f"Touch: Bereit (Hell={self.brightness}%)", WHITE, background=NAVY)
        
        # Canvas
        self.draw_canvas()
        
        # Buttons
        for btn in self.buttons:
            self.draw_button(btn)

    def check_button(self, sx, sy):
        for btn in self.buttons:
            if btn["x"] <= sx <= (btn["x"] + btn["w"]) and btn["y"] <= sy <= (btn["y"] + btn["h"]):
                return btn
        return None

    def run(self):
        self.draw_ui()
        self.beep(2500, 100)
        print("[AZ-Touch] Running with inverted PWM backlight & calibrated touch!")

        was_touched = False

        while True:
            touched, sx, sy, rx, ry = self.get_touch_pos()

            if touched:
                was_touched = True
                status_text = f"Touch: X={sx:03d} Y={sy:03d} (R:{rx},{ry})   "
                self.display.draw_text8x8(10, 48, status_text, YELLOW, background=NAVY)

                btn = self.check_button(sx, sy)
                if btn is not None:
                    self.draw_button(btn, pressed=True)
                    self.beep(3200, 60)
                    
                    if btn["id"] == "BEEP":
                        self.beep(3800, 120)
                    elif btn["id"] == "LIGHT":
                        self.cycle_brightness()
                    elif btn["id"] == "COLOR":
                        self.color_idx = (self.color_idx + 1) % len(self.theme_colors)
                        self.draw_ui()
                    elif btn["id"] == "CLEAR":
                        self.draw_canvas()
                        
                    time.sleep_ms(180)
                    self.draw_button(btn, pressed=False)
                else:
                    # Draw in canvas area
                    if 10 <= sx <= 310 and 68 <= sy <= 176:
                        self.display.fill_rectangle(sx-2, sy-2, 5, 5, YELLOW)
                        self.display.draw_pixel(sx, sy, RED)

                time.sleep_ms(20)
            else:
                if was_touched:
                    was_touched = False
                    self.display.draw_text8x8(10, 48, f"Touch: Bereit (Hell={self.brightness}%)", WHITE, background=NAVY)
                time.sleep_ms(15)

def start():
    app = AZTouchApp(initial_brightness=50)
    app.run()

if __name__ == "__main__":
    start()

"""XPT2046 Touch module."""
from time import sleep
from micropython import const  # type: ignore


class Touch(object):
    """Serial interface for XPT2046 Touch Screen Controller."""

    # Command constants from datasheet
    GET_X = const(0b11010000)  # X position (0x90 or 0xD0)
    GET_Y = const(0b10010000)  # Y position (0x90 or 0xD0)
    GET_Z1 = const(0b10110000)  # Z1 position
    GET_Z2 = const(0b11000000)  # Z2 position

    def __init__(self, spi, cs, int_pin=None, int_handler=None,
                 width=320, height=240,
                 x_min=200, x_max=1900, y_min=200, y_max=1900):
        self.spi = spi
        self.cs = cs
        self.cs.init(self.cs.OUT, value=1)
        self.rx_buf = bytearray(3)
        self.tx_buf = bytearray(3)
        self.width = width
        self.height = height
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.x_multiplier = width / (x_max - x_min)
        self.x_add = x_min * -self.x_multiplier
        self.y_multiplier = height / (y_max - y_min)
        self.y_add = y_min * -self.y_multiplier

        self.int_pin = int_pin
        if int_pin is not None:
            self.int_pin.init(int_pin.IN)
            self.int_handler = int_handler
            self.int_locked = False
            if int_handler is not None:
                int_pin.irq(trigger=int_pin.IRQ_FALLING | int_pin.IRQ_RISING,
                            handler=self.int_press)

    def is_touched(self):
        """Check if IRQ pin indicates touch (active LOW)."""
        if self.int_pin is not None:
            return self.int_pin.value() == 0
        return True

    def get_touch(self):
        """Read normalized touch coordinates."""
        if not self.is_touched():
            return None
        raw = self.raw_touch()
        if raw is not None:
            return self.normalize(*raw)
        return None

    def int_press(self, pin):
        """Send X,Y values to passed interrupt handler."""
        if not pin.value() and not self.int_locked:
            self.int_locked = True
            buff = self.raw_touch()
            if buff is not None and self.int_handler is not None:
                x, y = self.normalize(*buff)
                self.int_handler(x, y)
            sleep(.05)
        elif pin.value() and self.int_locked:
            sleep(.05)
            self.int_locked = False

    def normalize(self, x, y):
        """Normalize mean X,Y values to match LCD screen."""
        nx = int(self.x_multiplier * x + self.x_add)
        ny = int(self.y_multiplier * y + self.y_add)
        return nx, ny

    def raw_touch(self):
        """Read raw X,Y touch values."""
        x = self.send_command(self.GET_X)
        y = self.send_command(self.GET_Y)
        if self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max:
            return (x, y)
        return None

    def send_command(self, command):
        """Write command to XPT2046 and read 12-bit response."""
        self.tx_buf[0] = command
        self.tx_buf[1] = 0
        self.tx_buf[2] = 0
        self.cs(0)
        self.spi.write_readinto(self.tx_buf, self.rx_buf)
        self.cs(1)
        return (self.rx_buf[1] << 4) | (self.rx_buf[2] >> 4)

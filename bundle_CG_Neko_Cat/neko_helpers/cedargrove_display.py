# SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# cedargrove_display.py  2022-04-04 v0.0404  Cedar Grove Studios

import board
import digitalio
import displayio
import time


class Display:
    """ The Display class permits add-on displays to appear and act the same as
    built-in displays. Instantiates the display and touchscreen as specified by
    the `name` string and the touchscreen zero-rotation `calibration` value.
    Display brightness may not be supported on some displays.

    To do: Change touchscreen initialization for various rotation values.
           Use list or dictionary approach for display names and parameters."""

    def __init__(self, name="", rotation=0, calibration=None, brightness=1):

        if "DISPLAY" and "TOUCH" in dir(board):
            display_name = "built-in"
        else:
            display_name = name

        _calibration = calibration
        _brightness = brightness

        # Need to fix built-in touchscreen instantiation for other than
        # 0-degree rotation.
        _rotation = rotation

        # Instantiate the screen
        print(f"* Instantiate the {display_name} display")
        if display_name in "built-in":
            import adafruit_touchscreen

            self.display = board.DISPLAY
            self.display.rotation = _rotation
            self.display.brightness = _brightness

            # add rotation stuff here
            self.ts = adafruit_touchscreen.Touchscreen(
                board.TOUCH_XL,
                board.TOUCH_XR,
                board.TOUCH_YD,
                board.TOUCH_YU,
                calibration=_calibration,
                size=(self.display.width, self.display.height),
            )

        elif display_name in 'TFT FeatherWing - 2.4-inch 320x240 Touchscreen':
            import adafruit_ili9341
            import adafruit_stmpe610
            import pwmio

            # Brightness PWM frequency is not critical for this display
            self.lite = pwmio.PWMOut(board.D4, frequency=500)
            self.lite.duty_cycle = int(_brightness * 0xFFFF)

            displayio.release_displays()  # Release display resources
            display_bus = displayio.FourWire(
                board.SPI(), command=board.D10, chip_select=board.D9, reset=None
            )
            self.display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
            self.display.rotation = rotation
            ts_cs = digitalio.DigitalInOut(board.D6)
            self.ts = adafruit_stmpe610.Adafruit_STMPE610_SPI(
                board.SPI(),
                ts_cs,
                calibration=_calibration,
                size=(self.display.width, self.display.height),
                disp_rotation=_rotation,
                touch_flip=(False, False),
            )

        elif display_name in 'TFT FeatherWing - 3.5-inch 480x320 Touchscreen':
            import adafruit_hx8357
            import adafruit_stmpe610
            import pwmio

            # For brightness linearity, PWM frequency must be less than 1000Hz
            #   per the FAN5333B backlight LED controller datasheet
            self.lite = pwmio.PWMOut(board.D4, frequency=500)
            self.lite.duty_cycle = int(_brightness * 0xFFFF)

            displayio.release_displays()  # Release display resources
            display_bus = displayio.FourWire(
                board.SPI(), command=board.D10, chip_select=board.D9, reset=None
            )
            self.display = adafruit_hx8357.HX8357(display_bus, width=480, height=320)
            self.display.rotation = _rotation
            ts_cs = digitalio.DigitalInOut(board.D6)
            self.ts = adafruit_stmpe610.Adafruit_STMPE610_SPI(
                board.SPI(),
                ts_cs,
                calibration=_calibration,
                size=(self.display.width, self.display.height),
                disp_rotation=_rotation,
                touch_flip=(False, True),
            )
        else:
            print(f"*** ERROR: display {display_name} not defined")

    @property
    def brightness(self):
        """The display brightness level from 0.0 (dim) to 1.0 (bright).
        :param float new_brightness:
        """
        try:
            level = self.display.brightness
        except:
            try:
                level = self.lite.duty_cycle / 0xFFFF
            except:
                level = 1.0
        return level

    @brightness.setter
    def brightness(self, new_brightness):
        new_brightness = min(max(new_brightness, 0), 1.0)
        try:
            self.display.brightness = new_brightness
        except:
            try:
                self.lite.duty_cycle = int(new_brightness * 0xFFFF)
            except:
                raise RuntimeError('** Display brightness not adjustable')
                return

    @property
    def width(self):
        """The width (x) of the display in pixels.
        :param integer width:
        """
        return self.display.width

    @width.setter
    def width(self, new_width):
        self.display.width = new_width

    @property
    def height(self):
        """The height (y) of the display in pixels.
        :param integer height:
        """
        return self.display.height

    @height.setter
    def height(self, new_height):
        self.display.height = new_height

    @property
    def rotation(self):
        """The display rotation value in degrees.
        :param integer new_value
        """
        return self.display._rotation

    @rotation.setter
    def rotation(self, new_rotation):
        self.display.rotation = new_rotation

    def dim(self, new_brightness):
        """Gradually dim the display to a new brightness level.
        :param float new_brightness:
        """
        while self.brightness > new_brightness:
            self.brightness -= 0.04
            time.sleep(0.1)
        return True

    def brighten(self, new_brightness):
        """Gradually brighten the display to a new brightness level.
        :param float new_brightness:
        """
        while self.brightness < new_brightness:
            self.brightness += 0.04
            time.sleep(0.1)
        return False

    def show(self, group):
        self.display.show(group)
        return

    def color_brightness(self, bright, color):
        r = int(bright * ((color & 0xFF0000) >> 16))
        g = int(bright * ((color & 0x00FF00) >> 8))
        b = int(bright * ((color & 0x0000FF) >> 0))
        return (r << 16) + (g << 8) + b

    def screen_to_rect(self, width_factor=0, height_factor=0):
        """Convert normalized screen position input (0.0 to 1.0) to the display's
        rectangular pixel position."""
        return int(self.display.width * width_factor), int(self.display.height * height_factor)

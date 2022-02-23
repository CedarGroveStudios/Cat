# SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# cedargrove_display.py  2022-02-22 v0.0222  Cedar Grove Studios

import board
import busio
import digitalio
import displayio


class Display:
    """ The Display class permits add-on displays to appear and act the same as
    built-in displays. Instantiates the display and touchscreen as specified by
    the `name` string and the touchscreen zero-rotation `calibration` value.
    Display brightness may not be supported on some displays.

    To do: Change touchscreen initialization to accomodate various rotation
           values.
           Convert to list or dictionary-centric approach to managing display
           names and parameters."""

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

        elif display_name in 'TFT FeatherWing - 2.4" 320x240 Touchscreen':
            import adafruit_ili9341
            import adafruit_stmpe610

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

        elif display_name in 'TFT FeatherWing - 3.5" 480x320 Touchscreen':
            import adafruit_hx8357
            import adafruit_stmpe610

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
        try:
            level = self.display.brightness
        except:
            level = 1.0
        return level

    @brightness.setter
    def brightness(self, level):
        try:
            self.display.brightness = level
        except:
            print("** WARNING: Display brightness not adjustable")

    @property
    def width(self):
        return self.display.width

    @width.setter
    def width(self, value):
        self.display.width = value

    @property
    def height(self):
        return self.display.height

    @height.setter
    def height(self, value):
        self.display.height = value

    @property
    def rotation(self):
        return self.display._rotation

    @rotation.setter
    def rotation(self, value):
        self.display.rotation = value

    def show(self, group):
        self.display.show(group)
        return

    def screen_to_rect(self, width_factor=0, height_factor=0):
        """Convert normalized screen position input (0.0 to 1.0) to the display's
        rectangular pixel position."""
        return int(self.display.width * width_factor), int(self.display.height * height_factor)

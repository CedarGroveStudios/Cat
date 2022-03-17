# SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# neko_configuration.py  2022-02-22 v0.0222  Cedar Grove Studios


class Configuration:
    # specify display and touchscreen device using some unique characters
    #   from the display name

    """# built-in display
    DISPLAY_NAME = "built-in"
    CALIBRATION = ((5200, 59000), (5800, 57000))
    ROTATION = 0"""

    # TFT FeatherWing - 2.4" 320x240 Touchscreen
    DISPLAY_NAME = "2.4"
    CALIBRATION = ((277, 3872), (357, 3685))
    ROTATION = 0
    DISPLAY_BRIGHTNESS = 0.2

    # TFT FeatherWing - 3.5" 480x320 Touchscreen
    """DISPLAY_NAME = "3.5"
    CALIBRATION = ((214, 3879), (421, 3775))
    ROTATION = 0"""

    # display background color hex notation
    BACKGROUND_COLOR = 0x007070

    # how long to wait between animation frames in seconds
    ANIMATION_TIME = 0.3

    # whether to use a touch overlay
    USE_TOUCH_OVERLAY = True

    # how long to wait for next valid touch event in seconds
    TOUCH_COOLDOWN = 0.1

    # laser dot color in hex notation
    LASER_DOT_COLOR = 0xFF0000

    # cat color table
    CAT_COLORS = [
        0x000001,  # black
        0x808080,  # gray
        0xF0A000,  # orange
        0xF0F000,  # yellow
        0x8080FF,  # blue
        ]

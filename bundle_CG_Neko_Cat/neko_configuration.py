# SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# neko_configuration.py  2022-04-02 v0.0402  Cedar Grove Studios


class Configuration:
    # specify display and touchscreen device using some unique characters
    #   from the display name

    # Number of on-screen cats; maximum of 6
    CAT_QUANTITY = 6

    # cat color table
    CAT_COLORS = [
        0xFFFFFF,  # white
        0x000001,  # black
        0x808080,  # gray
        0xF0A000,  # orange
        0xF0F000,  # yellow
        0x8080FF,  # blue
        0xF000A0,  # purple
        ]

    # laser dot color in hex notation
    LASER_DOT_COLOR = 0xFF0000

    # display background color hex notation
    BACKGROUND_COLOR = 0x801080

    # how long to wait between animation frames in seconds
    ANIMATION_TIME = 0.3

    # How long before the display sleeps (seconds)
    DISPLAY_ACTIVE_TIME = 2 * 60

    # How long before the automatically reawakens (seconds)
    DISPLAY_SLEEP_TIME = 30 * 60

    # built-in display
    DISPLAY_NAME = "built-in"
    CALIBRATION = ((5200, 59000), (5800, 57000))
    ROTATION = 0
    DISPLAY_BRIGHTNESS = 1.0

    """# TFT FeatherWing - 2.4" 320x240 Touchscreen
    DISPLAY_NAME = "2.4-inch"
    CALIBRATION = ((277, 3872), (357, 3685))
    ROTATION = 0
    DISPLAY_BRIGHTNESS = 1.0"""

    # TFT FeatherWing - 3.5" 480x320 Touchscreen
    """DISPLAY_NAME = "3.5-inch"
    CALIBRATION = ((214, 3879), (421, 3775))
    ROTATION = 0
    DISPLAY_BRIGHTNESS = 1.0"""

    # whether to use a touch overlay
    USE_TOUCH_OVERLAY = True

    # how long to wait for next valid touch event in seconds
    TOUCH_COOLDOWN = 0.1

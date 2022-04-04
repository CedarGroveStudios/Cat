# SPDX-FileCopyrightText: 2022 TimCocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# Cedar Grove display, screensaver, and config changes: 2022-04-03 v0.0403

import gc
import time
import board
import displayio
import random
import vectorio
import adafruit_imageload
import neopixel
import neko_helpers.cedargrove_display as cedargrove_display
from neko_configuration import Configuration as config
from neko_helpers.neko import NekoAnimatedSprite

display = cedargrove_display.Display(
    name=config.DISPLAY_NAME,
    calibration=config.CALIBRATION,
    brightness= config.DISPLAY_BRIGHTNESS,
)
ts = display.ts

neo = neopixel.NeoPixel(board.NEOPIXEL, 1)
neo[0] = display.color_brightness(config.DISPLAY_BRIGHTNESS / 5, config.BACKGROUND_COLOR)

# variable to store the timestamp of previous touch event
LAST_TOUCH_TIME = -1

# create displayio Group
main_group = displayio.Group()
cat_group = displayio.Group()

# create background group, seperate from main_group so that
# it can be scaled, which saves RAM.
background_group = displayio.Group(scale=max(display.width, display.height) // 20)

# create bitmap to hold solid color background
background_bitmap = displayio.Bitmap(20, 15, 1)

# create background palette
background_palette = displayio.Palette(1)

# set the background color into the palette
background_palette[0] = config.BACKGROUND_COLOR

# create a tilegrid to show the background bitmap
background_tilegrid = displayio.TileGrid(
    background_bitmap, pixel_shader=background_palette
)

# append the tilegrid to the group.
background_group.append(background_tilegrid)

# add background_group to main_group
main_group.append(background_group)

gc.collect()

# Create a herd of cats (maximum of 6)
nekos = []
nekos_paletts = []
config.CAT_QUANTITY = min(max(0, config.CAT_QUANTITY), 6)
for i in range(config.CAT_QUANTITY):
    # Load the sprite sheet bitmap and palette
    sprite_sheet, _ = adafruit_imageload.load(
        "/neko_helpers/neko_cat_spritesheet.bmp",
        bitmap=displayio.Bitmap,
        palette=displayio.Palette,
    )
    # Create a unique palette for each cat
    nekos_paletts.append(_)
    color = config.CAT_COLORS[i]
    # Set dimmed outline color based on inverted fill color
    outline = display.color_brightness(0.6, color ^ 0xFFFFFF)
    # Instantiate Neko sprite class for each cat and slighly randomize animation time
    animation_time = config.ANIMATION_TIME + (random.randrange(-15, 15) / 100)
    nekos.append(NekoAnimatedSprite(
        animation_time=animation_time, display_size=(display.width, display.height),
        fill=color,
        outline=outline,
        sprites=sprite_sheet,
        palette=nekos_paletts[i],
    ))
    nekos[i].x = display.width // 2 - nekos[i].TILE_WIDTH // 2
    nekos[i].y = display.height // 2 - nekos[i].TILE_HEIGHT // 2
    cat_group.append(nekos[i])

# Sort the group based on sort_key (y coordinate and color)
cat_group.sort(key=lambda cat: cat.sort_key)
# Add the cat group
main_group.append(cat_group)

# Darken the display and NeoPixel then show the main_group
display.brightness = 0
neo[0] = display.color_brightness(display.brightness / 5, config.BACKGROUND_COLOR)
display.show(main_group)

if config.USE_TOUCH_OVERLAY:
    # initialize laser palette
    laser_dot_palette = displayio.Palette(1)
    # set the hex color code for the laser dot
    laser_dot_palette[0] = config.LASER_DOT_COLOR

    # create a circle to be the laser dot
    circle = vectorio.Circle(
        pixel_shader=laser_dot_palette,
        radius=3,
        x=-10,  # negative values so it starts off the edge of the display
        y=-10,  # won't get shown until the location moves onto the display
    )

    # add it to the main_group so it gets shown on the display when ready
    main_group.append(circle)

gc.collect()
print(f"free memory {gc.mem_free()/1000} kb")

_screensaver_start_time = time.monotonic()
_screensaver_state = "RESTORE"

while True:
    gc.collect()
    # update Nekos to do animations and movements
    for i in range(config.CAT_QUANTITY):
        nekos[i].update()

    # Bring lowest cats to the front; sort by y coordinate + color
    cat_group.sort(key=lambda cat: cat.sort_key)

    if config.USE_TOUCH_OVERLAY:
        # if HomeNeko (nekos[0]) is not moving to a location
        if not nekos[0].moving_to:
            # hide the laser dot circle by moving it off of the display
            circle.x = -10
            circle.y = -10

        _now = time.monotonic()

        # if the touch cooldown has elapsed since previous touch event
        if _now > LAST_TOUCH_TIME + config.TOUCH_COOLDOWN:

            # read current touch data from overlay
            touch_location = ts.touch_point

            # if anything is being touched
            if touch_location:
                if _screensaver_state in ("DIMMED", "DIM"):
                    # Restore screen brightness if touched if dimming or dimmed
                    _screensaver_state = "RESTORE"
                else:
                    # update the timestamp for touch cooldown enforcement
                    #   and reset the screensaver timer
                    LAST_TOUCH_TIME = _screensaver_start_time = _now

                    # move the laser dot circle to the x/y coordinates being touched
                    circle.x = touch_location[0]
                    circle.y = touch_location[1]

                    # print("placing laser dot at: {}".format(touch_location))

                    # tell Neko to move to the x/y coordinates being touched.
                    nekos[0].moving_to = (touch_location[0], touch_location[1])

    # Check the screensaver timer to see if it's time to dim display brightness
    if _screensaver_state == "ACTIVE" and time.monotonic() - _screensaver_start_time >= config.DISPLAY_ACTIVE_TIME:
        _screensaver_state = "DIM"
    # Check the screensaver timer to see if the display brightness should be restored
    if _screensaver_state == "DIMMED" and time.monotonic() - _screensaver_start_time >= config.DISPLAY_ACTIVE_TIME + config.DISPLAY_SLEEP_TIME:
        _screensaver_state = "RESTORE"

    # Gradually reduce display brightness while animating
    if _screensaver_state == "DIM":
        _new_brightness = max(display.brightness - 0.01, 0)
        display.brightness = _new_brightness
        neo[0] = display.color_brightness(_new_brightness / 5, config.BACKGROUND_COLOR)
        # When the target brightness is reached, set the state to DIMMED
        if display.brightness == 0:
            _screensaver_state = "DIMMED"

    # Gradually increase display brightness while animating
    if _screensaver_state == "RESTORE":
        _new_brightness = min(display.brightness + 0.01, config.DISPLAY_BRIGHTNESS)
        display.brightness = _new_brightness
        neo[0] = display.color_brightness(_new_brightness / 5, config.BACKGROUND_COLOR)
        # When the target brightness is reached, set the state to ACTIVE
        if display.brightness == config.DISPLAY_BRIGHTNESS:
            _screensaver_start_time = time.monotonic()
            _screensaver_state = "ACTIVE"

    # Print the display frame refresh rate (debug only)
    #print(f"frame: {time.monotonic() - _now} sec")

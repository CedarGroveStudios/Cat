# SPDX-FileCopyrightText: 2022 TimCocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# Cedar Grove display and config changes: 2022-03-17

"""Is there a way to perform an object deepcopy in CircuitPython? Trying to
create a mutable duplicate of a bitmap palette object within multiple class
instances that references a single pre-defined bitmap image."""

import gc
import time
import random
import board
import digitalio
import displayio
import vectorio
import adafruit_imageload
import neopixel
from random import randint
from rainbowio import colorwheel
import cedargrove_display
from neko_configuration import Configuration as config
from neko_helpers import NekoAnimatedSprite

BACKGROUND_COLOR = config.BACKGROUND_COLOR
DISPLAY_BRIGHTNESS = config.DISPLAY_BRIGHTNESS
ANIMATION_TIME = config.ANIMATION_TIME
USE_TOUCH_OVERLAY = config.USE_TOUCH_OVERLAY
TOUCH_COOLDOWN = config.TOUCH_COOLDOWN
LASER_DOT_COLOR = config.LASER_DOT_COLOR
CAT_QUANTITY = 5

#displayio.release_displays()

display = cedargrove_display.Display(
    name=config.DISPLAY_NAME,
    calibration=config.CALIBRATION,
    brightness= DISPLAY_BRIGHTNESS,
)

ts = display.ts

neo = neopixel.NeoPixel(board.NEOPIXEL, 1)
neo[0] = display.color_brightness(DISPLAY_BRIGHTNESS / 5, BACKGROUND_COLOR)


# variable to store the timestamp of previous touch event
LAST_TOUCH_TIME = -1

# create displayio Group
main_group = displayio.Group()

# create background group, seperate from main_group so that
# it can be scaled, which saves RAM.
background_group = displayio.Group(scale=max(display.width, display.height) // 20)

# create bitmap to hold solid color background
background_bitmap = displayio.Bitmap(20, 15, 1)

# create background palette
background_palette = displayio.Palette(1)

# set the background color into the palette
background_palette[0] = BACKGROUND_COLOR

# create a tilegrid to show the background bitmap
background_tilegrid = displayio.TileGrid(
    background_bitmap, pixel_shader=background_palette
)

# append the tilegrid to the group.
background_group.append(background_tilegrid)

# add background_group to main_group
main_group.append(background_group)

# create a herd of cats (maximum of 5)
nekos = []
nekos_paletts = []
CAT_QUANTITY = min(max(0, CAT_QUANTITY), 5)
for i in range(CAT_QUANTITY):
    # Load the sprite sheet bitmap and palette
    sprite_sheet, _ = adafruit_imageload.load(
        "/neko_cat_spritesheet.bmp",
        bitmap=displayio.Bitmap,
        palette=displayio.Palette,
    )
    nekos_paletts.append(_)
    color = config.CAT_COLORS[i]
    #print(f"cat {i} fill {hex(color)}  outline {hex(color ^ 0xffffff)}")
    outline = display.color_brightness(0.6, color ^ 0xffffff)  # invert and dim outline color
    nekos.append(NekoAnimatedSprite(
        animation_time=ANIMATION_TIME, display_size=(display.width, display.height),
        fill=color,
        outline=outline,
        sprites=sprite_sheet,
        palette=nekos_paletts[i],
    ))
    nekos[i].x = display.width // 2 - nekos[i].TILE_WIDTH // 2
    nekos[i].y = display.height // 2 - nekos[i].TILE_HEIGHT // 2
    main_group.append(nekos[i])

# create primary Neko
# Load the sprite sheet bitmap and palette
sprite_sheet, _ = adafruit_imageload.load(
    "/neko_cat_spritesheet.bmp",
    bitmap=displayio.Bitmap,
    palette=displayio.Palette,
)
neko = NekoAnimatedSprite(
    animation_time=ANIMATION_TIME, display_size=(display.width, display.height),
    fill=0xffffff,
    outline=0x000000,
    sprites=sprite_sheet,
    palette=_,
)

# put primary Neko in center of display
neko.x = display.width // 2 - neko.TILE_WIDTH // 2
neko.y = display.height // 2 - neko.TILE_HEIGHT // 2

# add primary neko to main_group
main_group.append(neko)

# show main_group on the display
display.show(main_group)

if USE_TOUCH_OVERLAY:
    # initialize laser palette
    laser_dot_palette = displayio.Palette(1)
    # set the hex color code for the laser dot
    laser_dot_palette[0] = LASER_DOT_COLOR

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
time.sleep(3)

while True:
    # update Neko to do animations and movements
    neko.update()

    for i in range(CAT_QUANTITY):
        nekos[i].update()

    if USE_TOUCH_OVERLAY:

        # if Neko is not moving to a location
        if not neko.moving_to:
            # hide the laser dot circle by moving it off of the display
            circle.x = -10
            circle.y = -10

        _now = time.monotonic()

        # if the touch cooldown has elapsed since previous touch event
        if _now > LAST_TOUCH_TIME + TOUCH_COOLDOWN:

            # read current touch data from overlay
            touch_location = ts.touch_point

            # if anything is being touched
            if touch_location:
                # update the timestamp for cooldown enforcement
                LAST_TOUCH_TIME = _now

                # move the laser dot circle to the x/y coordinates being touched
                circle.x = touch_location[0]
                circle.y = touch_location[1]

                # print("placing laser dot at: {}".format(touch_location))

                # tell Neko to move to the x/y coordinates being touched.
                neko.moving_to = (touch_location[0], touch_location[1])
        #print(f"frame: {time.monotonic() - _now} sec")


import time
import supervisor
import displayio
from adafruit_display_shapes.rect import Rect
from neko_helpers.color_spectrum_table import Spectrum
#from neko_helpers.color_spectrum import Spectrum
from neko_configuration import Configuration as config
import neko_helpers.cedargrove_display as cedargrove_display

# Instantiate the display and touchscreen
display = cedargrove_display.Display(
    name=config.DISPLAY_NAME,
    calibration=config.CALIBRATION,
    brightness= config.DISPLAY_BRIGHTNESS,
)
ts = display.ts

main_group = displayio.Group()

# about 264 colors before the pystack is exhausted
# first color will blend with last color unless mode="light"
VISIBLE_LIGHT = [
        0xff0000,
        #0xffff00,
        0x00ff00,
        #0x00ffff,
        0x0000ff,
        0x300040,
    ]

GAMMA = 1.8  # Best for TFT display

# Instantiate the background color spectrum
spectrum1 = Spectrum(VISIBLE_LIGHT, mode="normal", gamma=GAMMA)
spectrum2 = Spectrum(VISIBLE_LIGHT, mode="light", gamma=GAMMA)

neo_brightness = config.DISPLAY_BRIGHTNESS / 5

with_of_band = 2
granularity = display.width / with_of_band

# Define displayio rectangles
for i in range(granularity):
    color = 0x808080
    band = Rect(x=int(display.width / granularity * i), y=0, width=with_of_band, height=display.height//2, fill=color)
    main_group.append(band)


display.show(main_group)


"""time.sleep(1)
spectrum2.gamma = 1.8"""

tt0 = supervisor.ticks_ms()
for i in range(1001):
    color = spectrum2.color(0.5)
print(f"benchmark: {(supervisor.ticks_ms() - tt0)/1000:6.3f} msec")

while True:
    """print(f"mode: {spectrum1.mode}  gamma: {spectrum1.gamma:3.1f}")
    for i in range(granularity):
        color = spectrum1.color(i/granularity)
        main_group[i].fill = color

    time.sleep(3)"""

    #print(f"mode: {spectrum2.mode}  gamma: {spectrum2.gamma:3.1f}")
    for i in range(granularity):
        color = spectrum2.color(i/granularity)
        main_group[i].fill = color


    time.sleep(3)

# SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# color_spectrum.py  2022-04-05 v0.0405  Cedar Grove Studios

# n-Color Spectral Index to RGB Converter Helper


def map_range(x, in_min, in_max, out_min, out_max):
    """ Maps and constrains an input value from one range of values to another.
    (from adafruit_simpleio)

    :return: Returns value mapped to new range
    :rtype: float
    """
    in_range = in_max - in_min
    in_delta = x - in_min
    if in_range != 0:
        mapped = in_delta / in_range
    elif in_delta != 0:
        mapped = in_delta
    else:
        mapped = 0.5
    mapped *= out_max - out_min
    mapped += out_min
    if out_min <= out_max:
        return max(min(mapped, out_max), out_min)
    return min(max(mapped, out_max), out_min)


class Spectrum:
    """ Converts a spectral index value (0.0 to 1.0) of a graduated multicolor
    spectrum into an RGB color value. The multicolor spectrum is defined by a
    list of colors provided when the class is instantiated.
    Two spectrum modes are supported:
      Normal mode consists of a unique start and end color. An index of 0.0
      produces the first color; 1.0 produces the last color in the list.
      Wrap mode also continuously overlaps the list's first color and last color
      when the index value is near 0.0 and 1.0.
    A gamma value in range of 0.0 to 1.0 (1.0=linear) adjust color linearity. The
    default of 0.5 is usually helpful for color TFT displays.

    :param list colors:
    :param string mode:
    :param float gamma:

    to do:
      complete the "normal" spectral mode
    """
    def __init__(self, colors=None, mode="normal", gamma=0.5):
        self._number_of_colors = len(colors)
        if mode == "wrap":
            # Wrapped spectrum
            self._number_of_zones = self._number_of_colors
        else:
            # Normal spectrum
            self._number_of_zones = self._number_of_colors - 1

        self._gamma = gamma

        self._reds = [(r >> 16) & 0xFF for r in colors]
        self._grns = [(g >>  8) & 0xFF for g in colors]
        self._blus = [(b >>  0) & 0xFF for b in colors]

        self._zones = [(zone / self._number_of_colors, (zone + 1) / self._number_of_colors) for zone in range(int(self._number_of_colors))]


    def color(self, index=0):
        """ Converts a spectral index value to an RGB color value.

        :param float index:

        :return: Returns a 24-bit RGB value
        :rtype: integer
        """

        zone = int(self._number_of_colors * index)
        next_zone = (zone + 1) % self._number_of_colors
        zone_start = self._zones[zone][0]
        zone_end = self._zones[zone][1]

        red = map_range(index, zone_start, zone_end, self._reds[zone], self._reds[next_zone])
        grn = map_range(index, zone_start, zone_end, self._grns[zone], self._grns[next_zone])
        blu = map_range(index, zone_start, zone_end, self._blus[zone], self._blus[next_zone])

        red = int(round(red ** self._gamma, 0))
        grn = int(round(grn ** self._gamma, 0))
        blu = int(round(blu ** self._gamma, 0))

        return (int(red) << 16) + (int(grn) << 8) + int(blu)

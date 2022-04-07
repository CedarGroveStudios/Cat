# SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# color_spectrum.py  2022-04-06 v0.0406  Cedar Grove Studios

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
    """ Converts a spectral index value consisting of a positivive numeric value
    (0.0 to 1.0, modulus of 1.0) to an RGB color value that representing the
    index position on a graduated and blended multicolor spectrum.

    The spectrum is defined by a list of colors that are proportionally
    distributed across the spectrum.

    Two spectrum modes are supported:
      - "light" mode produces a spectrum that mimics a typical wavelength-of-light
        representation. The spectrum does not wrap; the first and last colors are
        not blended to each other.
      - "normal" mode blends the color list's first color and last color
        when the index value is near 0.0 and 1.0.

    A `gamma` value in the range of 0.0 to 1.0 will help to smooth the visual
    transition between colors. A value of 0.5 works well with TFT displays.

    :param list colors: A list of 24-bit color values. Up to 260 colors can be
                        included in the list, depending on available memory.
    :param string mode: Specifies the type of spectrum, "light" or "normal".
                        Defaults to "normal".
    :param float gamma: A positive float value to adjust color intensity for
                        human eye perception. Accepts a range of values between
                        0.0 and 3.0. Defaults to 0.5.

    to do:
      investigate adding gamma
    """
    def __init__(self, colors=None, mode="normal", gamma=0.5):
        self._colors = colors
        self._mode = mode
        self._gamma = min(max(gamma, 0), 3.0)
        self._index_granularity = (2 ** 16) - 1  # maximum index granularity

        # Select normal or "wavelength-of-light" -style spectrum
        if self._mode == "light":
            self._colors.insert(0, 0x000000)
        elif self._mode != "normal":
            raise ValueError("Incorrect mode; only 'normal' or 'light' allowed.")

        self._number_of_zones = len(self._colors)

        self._reds = [((r >> 16) & 0xFF) / 0xFF for r in colors]
        self._grns = [((g >>  8) & 0xFF) / 0xFF for g in colors]
        self._blus = [((b >>  0) & 0xFF) / 0xFF for b in colors]

        self._zones = [(zone / self._number_of_zones, (zone + 1) / self._number_of_zones) for zone in range(int(self._number_of_zones))]


    @property
    def mode(self):
        return self._mode

    @property
    def gamma(self):
        return self._gamma

    @gamma.setter
    def gamma(self, new_gamma=1.0):
        self._gamma = new_gamma

    def color(self, index=0):
        """ Converts a spectral index value to an RGB color value.

        :param float index:

        :return: Returns a 24-bit RGB value
        :rtype: integer
        """

        self._index = ((abs(index) * self._index_granularity) % self._index_granularity) / self._index_granularity

        zone = int(self._number_of_zones * index)
        next_zone = (zone + 1) % self._number_of_zones
        zone_start = self._zones[zone][0]
        zone_end = self._zones[zone][1]

        red = map_range(self._index, zone_start, zone_end, self._reds[zone], self._reds[next_zone])
        grn = map_range(self._index, zone_start, zone_end, self._grns[zone], self._grns[next_zone])
        blu = map_range(self._index, zone_start, zone_end, self._blus[zone], self._blus[next_zone])

        red = int(round((red ** self._gamma) * 0xFF, 0))
        grn = int(round((grn ** self._gamma) * 0xFF, 0))
        blu = int(round((blu ** self._gamma) * 0xFF, 0))

        return (int(red) << 16) + (int(grn) << 8) + int(blu)

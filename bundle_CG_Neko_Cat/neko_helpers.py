# SPDX-FileCopyrightText: 2022 TimCocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# Cedar Grove fill, outline, and sort key changes: 2022-04-01 v0.0401

import displayio
import time
import random


class NekoAnimatedSprite(displayio.TileGrid):
    # how many pixels the cat will move for each step
    CONFIG_STEP_SIZE = 10

    # how likely Neko is to stop moving to clean or sleep.
    # lower number means more likely to happen
    CONFIG_STOP_CHANCE_FACTOR = 30

    # how likely Neko is to start moving after scratching a wall.
    # lower number means more likely to happen
    CONFIG_START_CHANCE_FACTOR = 10

    # Minimum time to stop and scratch in seconds. larger time means scratch for longer
    CONFIG_MIN_SCRATCH_TIME = 2

    TILE_WIDTH = 32
    TILE_HEIGHT = 32

    # State object indexes
    _ID = 0
    _ANIMATION_LIST = 1
    _MOVEMENT_STEP = 2

    # last time an animation occurred
    LAST_ANIMATION_TIME = -1

    # index of the sprite within the currently running animation
    CURRENT_ANIMATION_INDEX = 0

    # last time the cat changed states
    # used to enforce minimum scratch time
    LAST_STATE_CHANGE_TIME = -1

    # State objects
    # Format: (ID, (Animation List), (Step Sizes))
    STATE_SITTING = (0, (0,), (0, 0))

    # Moving states
    STATE_MOVING_LEFT = (1, (20, 21), (-CONFIG_STEP_SIZE, 0))
    STATE_MOVING_UP = (2, (16, 17), (0, -CONFIG_STEP_SIZE))
    STATE_MOVING_RIGHT = (3, (12, 13), (CONFIG_STEP_SIZE, 0))
    STATE_MOVING_DOWN = (4, (8, 9), (0, CONFIG_STEP_SIZE))
    STATE_MOVING_UP_RIGHT = (
        5,
        (14, 15),
        (CONFIG_STEP_SIZE // 2, -CONFIG_STEP_SIZE // 2),
    )
    STATE_MOVING_UP_LEFT = (
        6,
        (18, 19),
        (-CONFIG_STEP_SIZE // 2, -CONFIG_STEP_SIZE // 2),
    )
    STATE_MOVING_DOWN_LEFT = (
        7,
        (22, 23),
        (-CONFIG_STEP_SIZE // 2, CONFIG_STEP_SIZE // 2),
    )
    STATE_MOVING_DOWN_RIGHT = (
        8,
        (10, 11),
        (CONFIG_STEP_SIZE // 2, CONFIG_STEP_SIZE // 2),
    )

    # Scratching states
    STATE_SCRATCHING_LEFT = (9, (30, 31), (0, 0))
    STATE_SCRATCHING_RIGHT = (10, (26, 27), (0, 0))
    STATE_SCRATCHING_DOWN = (11, (24, 25), (0, 0))
    STATE_SCRATCHING_UP = (12, (28, 29), (0, 0))

    # Other states
    STATE_CLEANING = (13, (0, 0, 1, 1, 2, 3, 2, 3, 1, 1, 2, 3, 2, 3, 0, 0, 0), (0, 0))
    STATE_SLEEPING = (
        14,
        (
            0,
            0,
            4,
            4,
            4,
            0,
            0,
            4,
            4,
            4,
            0,
            0,
            5,
            6,
            5,
            6,
            5,
            6,
            5,
            6,
            5,
            6,
            7,
            7,
            0,
            0,
            0,
        ),
        (0, 0),
    )

    # these states count as "moving"
    # used to alternate between moving and non-moving states
    MOVING_STATES = (
        STATE_MOVING_UP,
        STATE_MOVING_DOWN,
        STATE_MOVING_LEFT,
        STATE_MOVING_RIGHT,
        STATE_MOVING_UP_LEFT,
        STATE_MOVING_UP_RIGHT,
        STATE_MOVING_DOWN_LEFT,
        STATE_MOVING_DOWN_RIGHT,
    )

    # current state private field
    _CURRENT_STATE = STATE_SITTING

    # list of sprite indexes for the currently running animation
    CURRENT_ANIMATION = _CURRENT_STATE[_ANIMATION_LIST]

    """
    Neko Animated Cat Sprite. Extends displayio.TileGrid manages changing the visible
    sprite image to animate Neko in it's various states. Also manages moving Neko's location
    by the step size in the direction Neko is facing.

    :param float animation_time: How long to wait in-between animation frames. Unit is seconds.
     default is 0.3 seconds
    :param tuple display_size: Tuple containing width and height of display.
     Defaults to values from board.DISPLAY. Used to determine when we are at the edge
     of the display, so we know to start scratching.
    :param integer fill: Integer value representing 24-bit RGB fill color value.
    :param integer outline: Integer value representing 24-bit RGB outline color value.
    :param displayio.sprite_sheet sprites: Bitmap sprite sheet object.
    :param displayio.palette palette: Palette object for sprite sheet.
    """

    def __init__(self, animation_time=0.3, display_size=None, fill=None,
        outline=None, sprites=None, palette=None,
        ):

        self._display_size = display_size
        self._moving_to = None

        self._sprite_sheet = sprites
        self._neko_palette = palette

        if fill:
            self._neko_palette[5] = fill

        if outline:
            self._neko_palette[1] = outline

        # make the first color transparent
        self._neko_palette.make_transparent(0)

        # Create a sprite tilegrid as self
        super().__init__(
            self._sprite_sheet,
            pixel_shader=self._neko_palette,
            width=1,
            height=1,
            tile_width=32,
            tile_height=32,
        )

        # default initial location is top left corner
        self.x = 0
        self.y = 0

        # set the animation time into a private field
        self._animation_time = animation_time

    def _advance_animation_index(self):
        """
        Helper function to increment the animation index, and wrap it back around to
        0 after it reaches the final animation in the list.
        :return: None
        """
        self.CURRENT_ANIMATION_INDEX += 1
        if self.CURRENT_ANIMATION_INDEX >= len(self.CURRENT_ANIMATION):
            self.CURRENT_ANIMATION_INDEX = 0

    @property
    def moving_to(self):
        """
        Tuple with x/y location we are moving towards or none if
        not moving to anywhere specific.

        :return Optional(tuple): moving_to
        """
        return self._moving_to

    @moving_to.setter
    def moving_to(self, new_moving_to):

        # if new values is not None
        if new_moving_to:
            # initially start with the new value that is passed in
            _clamped_x = new_moving_to[0]
            _clamped_y = new_moving_to[1]

            # if x location of new value is within 1/2 tile size of left edge of display
            if new_moving_to[0] < self.TILE_WIDTH // 2 + 1:
                # override x to 1/2 tile size away from the left edge of display
                _clamped_x = self.TILE_WIDTH // 2 + 1

            # if x location of new value is within 1/2 tile size of right edge of display
            if new_moving_to[0] > self._display_size[0] - self.TILE_WIDTH // 2 - 1:
                # override x to 1/2 tile size away from right edge of display
                _clamped_x = self._display_size[0] - self.TILE_WIDTH // 2 - 1

            # if y location of new value is within 1/2 tile size of top edge of display
            if new_moving_to[1] < self.TILE_HEIGHT // 2 + 1:
                # override y to 1/2 tile size away from top edge
                _clamped_y = self.TILE_HEIGHT // 2 + 1
            # if y location of new value is within 1/2 tile size of bottom edge of display
            if new_moving_to[1] > self._display_size[1] - self.TILE_HEIGHT // 2 - 1:
                # override y to 1/2 tile size away from bottom edge
                _clamped_y = self._display_size[1] - self.TILE_HEIGHT // 2 - 1

            # update the moving to target location
            self._moving_to = (_clamped_x, _clamped_y)
        else:
            # None means not moving to a target location
            self._moving_to = None

    @property
    def sort_key(self):
        """
        Generate a sort key value based upon vertical position and fill
        color. Assumes that the color is unique to the class instance.

        :return: sort_key
        """
        return self.y + (self._neko_palette[5] / 0xF00000)

    @property
    def animation_time(self):
        """
        How long to wait in-between animation frames. Unit is seconds.

        :return: animation_time
        """
        return self._animation_time

    @animation_time.setter
    def animation_time(self, new_time):
        self._animation_time = new_time

    @property
    def current_state(self):
        """
        The current state object.
        Format: (ID, (Animation List), (Step Sizes))

        :return tuple: current state object
        """
        return self._CURRENT_STATE

    @current_state.setter
    def current_state(self, new_state):
        # only change if we aren't already in the new_state
        if self.current_state != new_state:
            # update the current state object
            self._CURRENT_STATE = new_state
            # update the current animation list
            self.CURRENT_ANIMATION = new_state[self._ANIMATION_LIST]
            # reset current animation index to 0
            self.CURRENT_ANIMATION_INDEX = 0
            # show the first sprite in the animation
            self[0] = self.CURRENT_ANIMATION[self.CURRENT_ANIMATION_INDEX]
            # update the last state change time
            self.LAST_STATE_CHANGE_TIME = time.monotonic()

    def animate(self):
        """
        If enough time has passed since the previous animation then
        execute the next animation step by changing the currently visible sprite and
        advancing the animation index.

        :return bool: True if an animation frame occurred. False if it's not time yet
         for an animation frame.
        """
        _now = time.monotonic()
        # is it time to do an animation step?
        if _now > self.LAST_ANIMATION_TIME + self.animation_time:
            # update the visible sprite
            self[0] = self.CURRENT_ANIMATION[self.CURRENT_ANIMATION_INDEX]
            # advance the animation index
            self._advance_animation_index()
            # update the last animation time
            self.LAST_ANIMATION_TIME = _now
            return True

        # Not time for animation step yet
        return False

    @property
    def is_moving(self):
        """
        Is Neko currently moving or not.

        :return bool: True if Neko is in a moving state. False otherwise.
        """
        return self.current_state in self.MOVING_STATES

    @property
    def center_point(self):
        """
        Current x/y coordinates Neko is centered on.

        :return tuple: x/y location of Neko's current center point:
        """
        return (self.x + self.TILE_WIDTH // 2, self.y + self.TILE_HEIGHT // 2)

    def update(self):
        # pylint: disable=too-many-branches,too-many-statements
        """
        Do the Following:
         - Attempt to do animation step.
         - Take a step if in a moving state.
         - Change states if needed.

        :return: None
        """
        _now = time.monotonic()

        # if neko is moving to a specific location (i.e. user touched a spot)
        if self.moving_to:

            # if the x of the target location is between the left and right edges of Neko
            if self.x < self.moving_to[0] < self.x + self.TILE_WIDTH:
                # if the y of the target location is between top and bottom edges of Neko
                if self.y < self.moving_to[1] < self.y + self.TILE_HEIGHT:
                    # change to either sleeping or cleaning states
                    self.current_state = random.choice(
                        (self.STATE_CLEANING, self.STATE_SLEEPING)
                    )
                    # clear the moving to target location
                    self.moving_to = None

            # if neko is moving to a specific location (i.e. user touched a spot)
            if self.moving_to:
                # if the target location is right of Neko
                if (
                    self.moving_to[0]
                    > self.center_point[0] + self.CONFIG_STEP_SIZE // 2
                ):
                    # if the target location is below Neko
                    if (
                        self.moving_to[1]
                        > self.center_point[1] + self.CONFIG_STEP_SIZE // 2
                    ):
                        # move down and to the right
                        self.current_state = self.STATE_MOVING_DOWN_RIGHT

                    # if the target location is above Neko
                    elif (
                        self.moving_to[1]
                        < self.center_point[1] - self.CONFIG_STEP_SIZE // 2
                    ):
                        # move up and to the right
                        self.current_state = self.STATE_MOVING_UP_RIGHT

                    # same Y position
                    else:
                        # move to the right
                        self.current_state = self.STATE_MOVING_RIGHT

                # if the target location is left of Neko
                elif (
                    self.moving_to[0]
                    < self.center_point[0] - self.CONFIG_STEP_SIZE // 2
                ):
                    # if the target location is below Neko
                    if (
                        self.moving_to[1]
                        > self.center_point[1] + self.CONFIG_STEP_SIZE // 2
                    ):
                        # move down and to the left
                        self.current_state = self.STATE_MOVING_DOWN_LEFT
                    # if the target location is above Neko
                    elif (
                        self.moving_to[1]
                        < self.center_point[1] - self.CONFIG_STEP_SIZE // 2
                    ):
                        # move up and to the left
                        self.current_state = self.STATE_MOVING_UP_LEFT

                    # same Y position
                    else:
                        # move to the left
                        self.current_state = self.STATE_MOVING_LEFT

                # same X position
                else:
                    # if the target location is below Neko
                    if (
                        self.moving_to[1]
                        > self.center_point[1] + self.CONFIG_STEP_SIZE // 2
                    ):
                        # move downwards
                        self.current_state = self.STATE_MOVING_DOWN
                    # if the target location is above Neko
                    elif (
                        self.moving_to[1]
                        < self.center_point[1] - self.CONFIG_STEP_SIZE // 2
                    ):
                        # move upwards
                        self.current_state = self.STATE_MOVING_UP

        # attempt animation
        did_animate = self.animate()

        # if we did do an animation step
        if did_animate:
            # if Neko is in a moving state
            if self.is_moving:
                # random chance to start sleeping or cleaning
                _roll = random.randint(0, self.CONFIG_STOP_CHANCE_FACTOR - 1)
                if _roll == 0:
                    # change to new state: sleeping or cleaning
                    _chosen_state = random.choice(
                        (self.STATE_CLEANING, self.STATE_SLEEPING)
                    )
                    self.current_state = _chosen_state
            else:  # cat is not moving

                # if we are currently in a scratching state
                if len(self.current_state[self._ANIMATION_LIST]) <= 2:

                    # check if we have scratched the minimum time
                    if (
                        _now
                        >= self.LAST_STATE_CHANGE_TIME + self.CONFIG_MIN_SCRATCH_TIME
                    ):
                        # minimum scratch time has elapsed

                        # random chance to start moving
                        _roll = random.randint(0, self.CONFIG_START_CHANCE_FACTOR - 1)
                        if _roll == 0:
                            # start moving in a random direction
                            _chosen_state = random.choice(self.MOVING_STATES)
                            self.current_state = _chosen_state

                else:  # if we are sleeping or cleaning

                    # if we have done every step of the animation
                    if self.CURRENT_ANIMATION_INDEX == 0:
                        # change to a random moving state
                        _chosen_state = random.choice(self.MOVING_STATES)
                        self.current_state = _chosen_state

            # If we are far enough away from side walls
            # to take a step in the current moving direction
            if (
                0
                <= (self.x + self.current_state[self._MOVEMENT_STEP][0])
                < (self._display_size[0] - self.TILE_WIDTH)
            ):

                # move the cat horizontally by current state step size x
                self.x += self.current_state[self._MOVEMENT_STEP][0]

            else:  # we ran into a side wall
                if self.x > self.CONFIG_STEP_SIZE:
                    # ran into right wall
                    self.x = self._display_size[0] - self.TILE_WIDTH - 1
                    # change state to scratching right
                    self.current_state = self.STATE_SCRATCHING_RIGHT
                else:
                    # ran into left wall
                    self.x = 1
                    # change state to scratching left
                    self.current_state = self.STATE_SCRATCHING_LEFT

            # If we are far enough away from top and bottom walls
            # to step in the current moving direction
            if (
                0
                <= (self.y + self.current_state[self._MOVEMENT_STEP][1])
                < (self._display_size[1] - self.TILE_HEIGHT)
            ):

                # move the cat vertically by current state step size y
                self.y += self.current_state[self._MOVEMENT_STEP][1]

            else:  # ran into top or bottom wall
                if self.y > self.CONFIG_STEP_SIZE:
                    # ran into bottom wall
                    self.y = self._display_size[1] - self.TILE_HEIGHT - 1
                    # change state to scratching down
                    self.current_state = self.STATE_SCRATCHING_DOWN
                else:
                    # ran into top wall
                    self.y = 1
                    # change state to scratching up
                    self.current_state = self.STATE_SCRATCHING_UP

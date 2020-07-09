#!/usr/bin/env python

import os

#
# application-wide consistent color definition
#

color = {
    'gray': (100, 100, 100),
    'black': (0, 0, 0),
    'red': (250, 0, 0),
    'green': (0, 250, 0),
    'light_green': (20, 60, 20),
    'background': (30, 30, 30),
    'urgent': (150, 50, 50),
    'white': (255, 255, 255),
    'help': (153, 255, 51),
    'info': (153, 255, 51),
    'danger': (60, 30, 30)
    }

instruction = "Press H to view help, SPACE to step, Q to quit"

help = """
  Wumpus World AI Demo Instructions

   H: Display this help info
   Space: Step
   C: Toggle auto/manual step mode
   V: Toggle view all mode
   R: Reset the world
   Q: Quit

   The bottom left light denotes busy
   when red, ready for next step when
   green.

        programmer: Wu Zhe 1070379096
"""

# Frames per second
fps = 20

# status light
light_flick_ticks = 5

# In auto mode, how many ticks to wait before generating next step
# event
wait_ticks = 10


status_font = (os.path.join('font', 'comic.ttf'), 26)
help_font = status_font


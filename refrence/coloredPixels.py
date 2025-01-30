# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
# SPDX-License-Identifier: MIT

import random
import time

import board
import displayio
import framebufferio
import rgbmatrix

# Release any previously active displays
displayio.release_displays()

def fill_grid_randomly(grid):
    """
    Fill the grid with random values based on the given fill fraction.
    
    Args:
        grid: The bitmap to fill.
    """
    for i in range(grid.height * grid.width):
        grid[i] = random.randint(0, 7)

# Initialize the RGB matrix display
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1
)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

# Set up display parameters
SCALE_FACTOR = 1
current_grid = displayio.Bitmap(display.width // SCALE_FACTOR, display.height // SCALE_FACTOR, 2)
next_grid = displayio.Bitmap(display.width // SCALE_FACTOR, display.height // SCALE_FACTOR, 2)
color_palette = displayio.Palette(8)  # Supports up to 8 colors
color_palette[0] = 0x000000  # Black
color_palette[1] = 0xFFFFFF  # White
color_palette[2] = 0xFF0000  # Red
color_palette[3] = 0x00FF00  # Green
color_palette[4] = 0x0000FF  # Blue
color_palette[5] = 0xFFFF00  # Yellow
color_palette[6] = 0xFF00FF  # Magenta
color_palette[7] = 0x00FFFF  # Cyan

current_tile_grid = displayio.TileGrid(current_grid, pixel_shader=color_palette)
next_tile_grid = displayio.TileGrid(next_grid, pixel_shader=color_palette)

# Create display groups
current_group = displayio.Group(scale=SCALE_FACTOR)
current_group.append(current_tile_grid)
display.root_group = current_group

next_group = displayio.Group(scale=SCALE_FACTOR)
next_group.append(next_tile_grid)

# Initial display setup

display.auto_refresh = True
time.sleep(3)
generation_cycles = 40

# Main animation loop
while True:
    # After the set generations, reset the grid with random values
    fill_grid_randomly(current_grid)
    

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

# Conway's Game of Life Rules:
# - Each cell has two states: alive (filled) or dead (empty).
# - Rules for determining the next state:
#   1. If a cell is alive and has 2 or 3 live neighbors, it stays alive.
#   2. If a cell is dead and has exactly 3 live neighbors, it becomes alive.
#   3. In all other cases, the cell becomes or remains dead.

def apply_game_of_life_rules(current_state, next_state):
    """
    Apply Conway's Game of Life rules to update the grid state.
    
    Args:
        current_state: The current bitmap representing the grid.
        next_state: The bitmap to store the next state of the grid.
    """
    grid_width = current_state.width
    grid_height = current_state.height

    for y in range(grid_height):
        y_offset = y * grid_width
        previous_row_offset = ((y + grid_height - 1) % grid_height) * grid_width
        next_row_offset = ((y + 1) % grid_height) * grid_width
        x_previous = grid_width - 1  # Start with the last column

        for x in range(grid_width):
            x_next = (x + 1) % grid_width
            # Calculate the number of live neighbors
            live_neighbors = (
                current_state[x_previous + previous_row_offset] + 
                current_state[x_previous + y_offset] + 
                current_state[x_previous + next_row_offset] +
                current_state[x + previous_row_offset] +
                current_state[x + next_row_offset] +
                current_state[x_next + previous_row_offset] +
                current_state[x_next + y_offset] +
                current_state[x_next + next_row_offset]
            )
            # Update the cell state based on Game of Life rules
            next_state[x + y_offset] = live_neighbors == 3 or (
                live_neighbors == 2 and current_state[x + y_offset]
            )
            x_previous = x

def fill_grid_randomly(grid, fill_fraction=0.33):
    """
    Fill the grid with random values based on the given fill fraction.
    
    Args:
        grid: The bitmap to fill.
        fill_fraction: The fraction of cells to make alive (default: 33%).
    """
    for i in range(grid.height * grid.width):
        grid[i] = random.random() < fill_fraction

def draw_conway_tribute(grid):
    """
    Fill the grid with a Conway tribute pattern based on xkcd's tribute.
    
    Args:
        grid: The bitmap to fill with the tribute pattern.
    """
    tribute_pattern = [
        b'  +++   ',
        b'  + +   ',
        b'  + +   ',
        b'   +    ',
        b'+ +++   ',
        b' + + +  ',
        b'   +  + ',
        b'  + +   ',
        b'  + +   ',
    ]
    # Clear the grid
    for i in range(grid.height * grid.width):
        grid[i] = 0
    # Draw the tribute pattern centered on the grid
    for i, row_data in enumerate(tribute_pattern):
        y = grid.height - len(tribute_pattern) - 2 + i
        for j, cell in enumerate(row_data):
            grid[(grid.width - 8) // 2 + j, y] = cell & 1

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
color_palette = displayio.Palette(2)
current_tile_grid = displayio.TileGrid(current_grid, pixel_shader=color_palette)
next_tile_grid = displayio.TileGrid(next_grid, pixel_shader=color_palette)

# Create display groups
current_group = displayio.Group(scale=SCALE_FACTOR)
current_group.append(current_tile_grid)
display.root_group = current_group

next_group = displayio.Group(scale=SCALE_FACTOR)
next_group.append(next_tile_grid)

# Initial display setup
color_palette[1] = 0xFFFFFF  # White for alive cells
draw_conway_tribute(current_grid)
display.auto_refresh = True
time.sleep(3)
generation_cycles = 40

# Main animation loop
while True:
    # Run multiple generations of Game of Life
    for _ in range(generation_cycles):
        display.root_group = current_group
        apply_game_of_life_rules(current_grid, next_grid)
        display.root_group = next_group
        apply_game_of_life_rules(next_grid, current_grid)

    # After the set generations, reset the grid with random values
    fill_grid_randomly(current_grid)
    # Choose a new random color for alive cells
    color_palette[1] = (
        (0x0000FF if random.random() > 0.33 else 0) |  # Blue
        (0x00FF00 if random.random() > 0.33 else 0) |  # Green
        (0xFF0000 if random.random() > 0.33 else 0)    # Red
    ) or 0xFFFFFF  # Default to white if no color is chosen
    generation_cycles = 40

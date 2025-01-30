import random
import time

import board
import displayio
import framebufferio
import rgbmatrix
import requests

url = "https://ai.hackclub.com/chat/completions"
headers = {
    "Content-Type": "application/json"
}
data = {
    "messages": [
        {
            "role": "user",
            "content": (
                "Generate a 32x64 pixel art design using only 8 colors: black (#000000), white (#FFFFFF), red (#FF0000), green (#00FF00), blue (#0000FF), yellow (#FFFF00), magenta (#FF00FF), and cyan (#00FFFF). The design should be visually interesting, abstract, and suitable for display on an RGB LED matrix. Make sure to represent the pixel data in a compact format, such as a 2D array of integers where each number represents a color index (0-7). Ensure the output is different and unique for every generation."
            )
        }
    ]
}

response = requests.post(url, headers=headers, json=data)

# Print the response
print(response.json())

# Release any previously active displays
displayio.release_displays()

def fill_grid_randomly(grid):
    """
    Fill the grid with random colors chosen from the palette.
    
    Args:
        grid: The bitmap to fill.
    """
    for i in range(grid.height * grid.width):
        grid[i] = random.randint(0, 7)  # Random index from 0 to 7

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
current_grid = displayio.Bitmap(display.width // SCALE_FACTOR, display.height // SCALE_FACTOR, 8)  # 8 colors
color_palette = displayio.Palette(8)  # Supports up to 8 colors
color_palette[0] = 0x000000  # Black
color_palette[1] = 0xFFFFFF  # White
color_palette[2] = 0xFF0000  # Red
color_palette[3] = 0x00FF00  # Green
color_palette[4] = 0x0000FF  # Blue
color_palette[5] = 0xFFFF00  # Yellow
color_palette[6] = 0xFF00FF  # Magenta
color_palette[7] = 0x00FFFF  # Cyan

# Create TileGrid with the current grid and palette
current_tile_grid = displayio.TileGrid(current_grid, pixel_shader=color_palette)

# Create the display group and add the TileGrid
current_group = displayio.Group(scale=SCALE_FACTOR)
current_group.append(current_tile_grid)
display.root_group = current_group

# Initial display setup
fill_grid_randomly(current_grid)  # Fill the grid with initial random colors
display.auto_refresh = True

# Main animation loop
while True:
    time.sleep(0.5)  # Pause before refreshing
    fill_grid_randomly(current_grid)  # Randomize colors for the next frame
    display.refresh()  # Refresh the display to show updates

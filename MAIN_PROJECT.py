import random
import time
import board
import displayio
import framebufferio
import rgbmatrix

import requests

def fetch_network_time():
    """Fetch EST time, return (hours, seconds_after_hour, timestamp)."""
    try:
        response = requests.get('http://worldtimeapi.org/api/timezone/America/New_York')
        if response.status_code == 200:
            data = response.json()
            datetime_str = data['datetime']
            hours = int(datetime_str[11:13])      # Hours (0-23)
            minutes = int(datetime_str[14:16])    # Minutes
            seconds = int(datetime_str[17:19])    # Seconds
            # Convert to seconds after hour
            seconds_after_hour = (minutes * 60) + seconds
            return (hours, seconds_after_hour, time.monotonic())
    except Exception as e:
        print(f"Error fetching time: {e}")
        return (0, 0, time.monotonic())
# Get initial time
initial_hours, initial_seconds_after_hour, initial_timestamp = fetch_network_time()

def get_current_time():
    """Return current (hours, seconds_after_hour) based on initial fetch."""
    elapsed = int(time.monotonic() - initial_timestamp)
    total_seconds = initial_seconds_after_hour + elapsed
    
    # Calculate current values
    hours_to_add = total_seconds // 3600
    current_seconds = total_seconds % 3600
    current_hours = (initial_hours + hours_to_add) % 24
    
    return (current_hours, current_seconds)

# Release any previously active displays
displayio.release_displays()

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

# Create two bitmaps
grid1 = displayio.Bitmap(display.width // SCALE_FACTOR, display.height // SCALE_FACTOR, 8)
grid2 = displayio.Bitmap(display.width // SCALE_FACTOR, display.height // SCALE_FACTOR, 8)

# Create color palette
color_palette = displayio.Palette(8)
color_palette[0] = 0x000000  # Black
color_palette[1] = 0x0000FF  # Blue
color_palette[2] = 0x00FFFF  # Cyan
color_palette[3] = 0x00FF00  # Green
color_palette[4] = 0xFFFFFF  # White
color_palette[5] = 0xFF00FF  # Magenta
color_palette[6] = 0xFF0000  # Red
color_palette[7] = 0xFFFF00  # Yellow

# Create TileGrids and Groups
tile_grid1 = displayio.TileGrid(grid1, pixel_shader=color_palette)
tile_grid2 = displayio.TileGrid(grid2, pixel_shader=color_palette)

group1 = displayio.Group(scale=SCALE_FACTOR)
group2 = displayio.Group(scale=SCALE_FACTOR)
group1.append(tile_grid1)
group2.append(tile_grid2)

display.root_group = group1
display.auto_refresh = True

def dropPixels(origonalGrid: displayio.Bitmap, newGrid:displayio.Bitmap):
    """
    Drop pixels down the screen.
    
    Args:
        origonalGrid: The bitmap that is being dropped on the `newGrid`.
        newGrid: The bitmap that the dropped pixels are being copied to.
    """
    # Start from bottom row and work up to avoid multiple drops in one pass
    for row in range(newGrid.height-1, -1, -1):  # Start from bottom row, go up
        for col in range(0, newGrid.width):  # Left to right
            newGrid[col, row] = origonalGrid[col, row]
            if newGrid[col, row] != 0 and row < newGrid.height-1 and newGrid[col, row+1] == 0:
                newGrid[col, row+1] = newGrid[col, row]
                newGrid[col, row] = 0

def newTimePixel(grid:displayio.Bitmap):
    """
    Add a new pixel to the top row of the grid.
    
    Args:
        grid: The bitmap to add the pixel to.
    """
    grid[random.randint(0, grid.width-1),0] = random.randint(1,7)  # Drop a pixel

def dropPixelsAndRefresh(source_grid: displayio.Bitmap, target_grid: displayio.Bitmap, target_group: displayio.Group):
    """Process one frame of animation and swap display groups."""
    start_time = time.monotonic()
    display.refresh()
    dropPixels(source_grid, target_grid)
    display.root_group = target_group  # Swap to show target group
    # newTimePixel(target_grid)
    elapsed = time.monotonic() - start_time
    if elapsed < 0.5:
        time.sleep(0.5 - elapsed)

hour = get_current_time()[0]
second = get_current_time()[1]
# Main loop
while True:
    dropPixelsAndRefresh(grid1, grid2, group2)
    dropPixelsAndRefresh(grid2, grid1, group1)
    
    current_hour, current_second = get_current_time()
    print(f"Current time: {current_hour}:{current_second}. Second: {second}")
    # Run newTimePixel every 2 seconds
    if current_second - second >= 2:
        newTimePixel(grid1)
        newTimePixel(grid2)
        second = current_second
    
    # Reset grid when hour changes
    if current_hour != hour:
        grid1.fill(0)
        grid2.fill(0)
        hour = current_hour


# Note to Cheru or whomever is reviewing this:
# I used the game of life demo code to start off of and then paired it down to what I needed. 
# Github copiolet added some of the nice documentation that I decided to keep do more of myself. 
# It took me a while to figure out a good way to display time that both looked nice and is understandable if you know how it works.
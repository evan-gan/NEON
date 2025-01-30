# A fun clock on a 64x32 LED matrix!
This project creates a esoteric visualization of time on a 64x32 LED matrix display. It works by:

- Dropping pixels across the display
- Color-coding pixels based on the current time
- Fetching network time from WorldTimeAPI
- Automatically resetting display every hour

## Implementation
The display uses different colors to represent different time periods within each hour. Pixels are added every few seconds and "fall" across the screen, creating a dynamic time visualization.

The code handles time synchronization, pixel animation, and display management through the CircuitPython displayio library. Frames are rendered 1/2 of a second before they are going to be displayed.
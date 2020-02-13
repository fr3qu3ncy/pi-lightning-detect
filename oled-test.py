# PiOLED testing - Micro Cube Technology

# General imports
import sys
import time
from datetime import datetime
# PiOLED imports
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

def disp_init():
    # PiOLED - initialise
    global disp
    global draw
    global image
    global width
    global height
    global top
    global bottom
    # Create the I2C interface.
    i2c = busio.I2C(SCL, SDA)
    # Create the SSD1306 OLED class.
    # The first two parameters are the pixel width and pixel height.  Change these
    # to the right size for your display!
    disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
    # Clear display.
    disp.fill(0)
    disp.show()
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    bottom = height-padding
    # Move left to right keeping track of the current x position for drawing shapes.
    global x
    x = 0
    # Load default font.
    global font
    global font1
    global font2
    global font3
    font = ImageFont.load_default()
    font1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 7)
    font2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    font3 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)

#PiOLED functions
def disp_clear():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
def disp_text(mesg, line, size, offset=0):
    if (size==7):
        typeface=font1
    elif (size==14):
        typeface=font2
    elif (size==28):
        typeface=font3
    else:
        typeface=font
    y=disp_get_y(line)
    draw.text((x, top+offset+y), mesg, font=typeface, fill=255)
    disp.image(image)
    disp.show()
def disp_get_y(line):
    switcher = {
        1: 0,
        2: 7,
        3: 14,
        4: 21
    }
    return switcher.get(line,0)

disp_init()
disp_clear()
disp_text("Init sensor sucess", 1, 7)
disp_text("Font Size 7", 2, 7)
disp_text("Indoor", 3, 0, 1)
disp_text("Disterbers on", 4, 0, 3)
input("Press Enter to continue...")
disp_clear()
disp_text("Detection started", 1, 14, -1)
disp_text("Font Size 14", 3, 14, -2)
disp_text("Font Size 7", 4, 7, 5)
input("Press Enter to continue...")
disp_clear()
disp_text("Detection started", 1, 14, -2)
disp_text("Font Size 14", 3, 14, -2)
disp_text("Font Size 8", 4, 0, 4)
input("Press Enter to continue...")
disp_clear()
disp_text("Detection started", 2, 14)
disp_text("Font Size 14", 4, 14)
disp_text("Font Size 7", 1, 7)
disp_clear()
input("Press Enter to continue...")
disp_text("Detection started", 2, 14, 1)
disp_text("Font Size 14", 4, 14)
disp_text("Font Size 7", 1, 7)
input("Press Enter to continue...")
disp_clear()
disp_text("Detection started", 2, 14, 1)
disp_text("Font Size 14", 4, 14)
disp_text("Font Size 8", 1, 0)
input("Press Enter to continue...")
disp_clear()
disp_text("Font Size 28", 2, 28, 1)
disp_text("Font Size 8", 1, 0)
input("Press Enter to continue...")
# Pi Lightning Detect - Micro Cube Technology
# OLED display functions for pi-l-detect

#####################
## DO NOT USE !!!! ##
#####################

# file pi_ld_oled_lib.py

# General imports
from pi_ld_lib import *
#import pi_ld_global
import time
from datetime import datetime, timedelta
import logging

# PiOLED imports
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# PiOLED functions
def display_init():
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
    # Create the SSD1306 OLED class. The first two parameters are the pixel width and pixel height.  Change these to the right size for your display!
    disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
    # Clear display.
    disp.fill(0)
    disp.show()
    # Create blank image for drawing. Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    # Define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    bottom = height-padding
    # Move left to right keeping track of the current x position for drawing shapes.
    global x
    x = 0
    # Load default font.
    global font
    global font_dvs_7
    global font_dvs_14
    global font_dvs_28
    global font_msd_8
    global font_msd_12
    global font_msd_16
    global font_msd_20
    
    font = ImageFont.load_default()
    font_dvs_7 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 7)
    font_dvs_14 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    font_dvs_28 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
    font_msd_8 = ImageFont.truetype('fonts/Museo Sans Display Light.ttf', 8)
    font_msd_12 = ImageFont.truetype('fonts/Museo Sans Display Light.ttf', 12)
    font_msd_16 = ImageFont.truetype('fonts/Museo Sans Display Light.ttf', 16)
    font_msd_20 = ImageFont.truetype('fonts/Museo Sans Display Light.ttf', 20)

    logging.info('Display initialised')

def display_clear():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

def display_stats_update():
    display_clear() # TODO will want to change this to only clear the stats area.
    typeface = font_msd_12
    mesg = "Last 10m  30m  1h"
    draw.text((x, top), mesg, font=typeface, fill=255)
    typeface = font_msd_16
    mesg = "Dis %s Eng %s",
    draw.text((x, top), mesg, font=typeface, fill=255)
    disp.image(image)
    disp.show()
    logging.info('Updated display')

def disp_text(mesg, line, size, offset=0):
    if (size == 7):
        typeface = font_dvs_7
    elif (size == 14):
        typeface = font_dvs_14
    elif (size == 28):
        typeface = font_dvs_28
    else:
        typeface = font
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
    return switcher.get(line, 0)

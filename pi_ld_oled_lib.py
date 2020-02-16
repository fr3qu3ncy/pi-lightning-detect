# Pi Lightning Detect - Micro Cube Technology
# OLED display functions for pi-l-detect

# file pi_ld_oled_lib.py

# General imports
from pi_ld_lib import *

# PiOLED imports
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

def display_update():
    logging.info('Updating display')
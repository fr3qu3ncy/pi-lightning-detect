# Pi Lightning Detect - Micro Cube Technology
# Control of AS3935 lightning sensor, and stsus updates to PiOLED display

# file DFRobot_AS3935_detailed.py
#
# SEN0290 Lightning Sensor
# This sensor can detect lightning and display the distance and intensity of the lightning within 40 km
# It can be set as indoor or outdoor mode.
# The module has three I2C, these addresses are:
# AS3935_ADD1  0x01   A0 = 1  A1 = 0
# AS3935_ADD2  0x02   A0 = 0  A1 = 1
# AS3935_ADD3  0x03   A0 = 1  A1 = 1
#
#
# Copyright    [DFRobot](http://www.dfrobot.com), 2018
# Copyright    GNU Lesser General Public License
#
# version  V1.0
# date  2018-11-28

# General imports
import sys
# sys.path.append('../')
import time
from datetime import datetime

# AS3935 imports
from DFRobot_AS3935_Lib import DFRobot_AS3935
import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BOARD)

# PiOLED imports
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# PiOLED - initialise
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
x = 0
# Load default font.
font = ImageFont.load_default()

# I2C address - AS3935
AS3935_I2C_ADDR1 = 0X01
AS3935_I2C_ADDR2 = 0X02
AS3935_I2C_ADDR3 = 0X03

#Antenna tuning capcitance (must be integer multiple of 8, 8 - 120 pf)
AS3935_CAPACITANCE = 96
IRQ_PIN = 4

# Not needed Adafruit lib set this to BCM
#GPIO.setmode(GPIO.BCM)

#PiOLED functions
def disp_clear():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
def disp_text(mesg, line):
    y=disp_get_y(line)
    draw.text((x, top+y), mesg, font=font, fill=255)
    disp.image(image)
    disp.show()
def disp_get_y(line):
    switcher = {
        1: 0,
        2: 8,
        3: 16,
        4: 24
    }
    return line

# AS2925 - initialise
disp_clear()
sensor = DFRobot_AS3935(AS3935_I2C_ADDR3, bus = 1)
if (sensor.reset()):
    print("init sensor sucess.")
    disp_text("Init sensor sucess.", 1)
else:
    print("init sensor fail")
    disp_text("Init sensor fail", 1)
    while True:
        pass
#Configure sensor
sensor.powerUp()

#set indoors or outdoors models
sensor.setIndoors()
disp_text("Indoor", 2)
#sensor.setOutdoors()

#disturber detection
sensor.disturberEn()
disp_text("Disterbers on", 3)
#sensor.disturberDis()

sensor.setIrqOutputSource(0)
time.sleep(0.5)
#set capacitance
sensor.setTuningCaps(AS3935_CAPACITANCE)

# Connect the IRQ and GND pin to the oscilloscope.
# uncomment the following sentences to fine tune the antenna for better performance.
# This will dispaly the antenna's resonance frequency/16 on IRQ pin (The resonance frequency will be divided by 16 on this pin)
# Tuning AS3935_CAPACITANCE to make the frequency within 500/16 kHz plus 3.5% to 500/16 kHz minus 3.5%
#
# sensor.setLcoFdiv(0)
# sensor.setIrqOutputSource(3)

#Set the noise level,use a default value greater than 7
sensor.setNoiseFloorLv1(2)
#noiseLv = sensor.getNoiseFloorLv1()

#used to modify WDTH,alues should only be between 0x00 and 0x0F (0 and 7)
sensor.setWatchdogThreshold(2)
#wtdgThreshold = sensor.getWatchdogThreshold()

#used to modify SREJ (spike rejection),values should only be between 0x00 and 0x0F (0 and 7)
sensor.setSpikeRejection(2)
#spikeRejection = sensor.getSpikeRejection()

#view all register data
#sensor.printAllRegs()

def callback_handle(channel):
    global sensor
    time.sleep(0.005)
    intSrc = sensor.getInterruptSrc()
    if intSrc == 1:
        lightningDistKm = sensor.getLightningDistKm()
        print('Lightning occurs!')
        print('Distance: %dkm'%lightningDistKm)

        lightningEnergyVal = sensor.getStrikeEnergyRaw()
        print('Intensity: %d '%lightningEnergyVal)
    elif intSrc == 2:
        print('Disturber discovered!')
    elif intSrc == 3:
        print('Noise level too high!')
    else:
        pass
#Set to input mode
GPIO.setup(IRQ_PIN, GPIO.IN)
#Set the interrupt pin, the interrupt function, rising along the trigger
GPIO.add_event_detect(IRQ_PIN, GPIO.RISING, callback = callback_handle)
print("start lightning detect.")
disp_text("Lightning detect started", 4)

while True:
    time.sleep(1.0)



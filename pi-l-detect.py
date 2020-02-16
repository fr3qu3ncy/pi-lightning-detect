# Pi Lightning Detect - Micro Cube Technology
# Control of AS3935 lightning sensor, and stsus updates to PiOLED display

# file pi-l-detect.py

# General imports
from pi_ld_lib import *

# AS3935 imports
from DFRobot_AS3935_Lib import DFRobot_AS3935
import RPi.GPIO as GPIO

# PiOLED imports
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Set up logging
format = "%(asctime)s.%(msecs)03d %(levelname)s %(process)d (%(name)s-%(threadName)s) %(message)s (linux-Thread-%(thread)d)"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%m/%d/%Y %H:%M:%S")
logging.info('pi-lightgning-detect started')

# Create in memeory database
db_create()

# PiOLED - initialise
# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)
# Create the SSD1306 OLED class. The first two parameters are the pixel width and pixel height. Change these to the right size for your display!
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
# Draw some shapes. First define some constants to allow easy resizing of
# shapes.
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
# Antenna tuning capcitance (must be integer multiple of 8, 8 - 120 pf)
AS3935_CAPACITANCE = 96
IRQ_PIN = 4

# PiOLED functions

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
        4: 25
    }
    return switcher.get(line, 0)

# Main thread
disp_clear()

# AS2925 - initialise
sensor = DFRobot_AS3935(AS3935_I2C_ADDR3, bus=1)
if (sensor.reset()):
    logging.info("Initialisation of sensor sucess.")
    disp_text("Init sensor sucess.", 1)
else:
    logging.info("Initialisation sensor fail")
    disp_text("Init sensor fail", 1)
    while True:
        pass
# Configure sensor
sensor.powerUp()
# Set indoors or outdoors models
sensor.setIndoors()
logging.info("Sensor set to indoor mode")
disp_text("Indoor", 2)
#sensor.setOutdoors()
#logging.info("Sensor set to outdoor mode")
#disp_text("Outdoor", 2)

# Disturber detection
sensor.disturberEn()
logging.info("Disterbers will be raised and logged")
disp_text("Disterbers on", 3)
#sensor.disturberDis()
#logging.info("Disterbers not raised")
#disp_text("Disterbers off", 3)

sensor.setIrqOutputSource(0)
time.sleep(0.5)
# Set capacitance
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
    disp_clear()
    global sensor
    time.sleep(0.005)
    intSrc = sensor.getInterruptSrc()
    if intSrc == 1:
        lightningDistKm = sensor.getLightningDistKm()
        lightningEnergyVal = sensor.getStrikeEnergyRaw()
        disp_text("** LIGHTNING **", 1)
        disp_text('Distance: %dkm'%lightningDistKm, 2)
        disp_text('Intensity: %d '%lightningEnergyVal, 3)
        #detected_lightning(lightningDistKm, lightningEnergyVal)
        updater_thread = threading.Thread(target=detected_lightning, args=[lightningDistKm, lightningEnergyVal])
        updater_thread.start()
    elif intSrc == 2:
        disp_text('Disturber discovered', 2)
        # detected_disterber()
        updater_thread = threading.Thread(target=detected_disturber)
        updater_thread.start()
    elif intSrc == 3:
        #disp_text('Noise level too high', 2)
        updater_thread = threading.Thread(target=detected_noise)
        updater_thread.start()
        detected_noise()
    else:
        disp_text('Distance algo updated', 2)
        #detected_algo_updated()
        updater_thread = threading.Thread(target=detected_algo_updated)
        updater_thread.start()
        pass

# pylint: disable=no-member
# Set IRQ pin to input mode
GPIO.setup(IRQ_PIN, GPIO.IN)
# Set the interrupt pin, the interrupt function, rising along the trigger
GPIO.add_event_detect(IRQ_PIN, GPIO.RISING, callback = callback_handle)
# pylint: enable=no-member

logging.info("Detection started...")
disp_text("Detection started", 4)

#TEST CODE
updater_thread = threading.Thread(target=detected_lightning, args=[31, 11])
updater_thread.start()
logging.info("Started thread : %s", updater_thread.name)
updater_thread = threading.Thread(target=detected_disturber)
updater_thread.start()
updater_thread = threading.Thread(target=detected_noise)
updater_thread.start()
updater_thread = threading.Thread(target=detected_algo_updated)
updater_thread.start()
time.sleep(1)
updater_thread = threading.Thread(target=detected_lightning, args=[27, 2])
updater_thread.start()
time.sleep(1)
updater_thread = threading.Thread(target=detected_lightning, args=[14, 22])
updater_thread.start()
time.sleep(0.2)
updater_thread = threading.Thread(target=detected_lightning, args=[14, 31])
updater_thread.start()
time.sleep(0.2)
print("Database Dump:")
db_dump('ld_lightning')
db_dump('ld_disturber')
db_dump('ld_noise')
db_dump('ld_algo')

while True:
    time.sleep(1.0)



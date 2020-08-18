# Pi Lightning Detect - Micro Cube Technology
# Functions for pi-l-detect

# file pi_ld_lib.py

#from pi_ld_oled_lib import *
#from pi_ld_global import *
import sys
import time
from datetime import datetime, timedelta
import logging
from logging.handlers import TimedRotatingFileHandler
import threading
import sqlite3

# PiOLED imports
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

global events_d        # Stores nubmer of disturber events in the past (10m, 30m, 1h, 24h, 30d)
global events_n        # Stores nubmer of noise events in the past (10m, 30m, 1h, 24h, 30d)
global events_a        # Stores nubmer of algo update events in the past (10m, 30m, 1h, 24h, 30d)
global events_l        # Stores nubmer of lightning strikes in the past (10m, 30m, 1h, 24h, 30d)
global events_last_distance # Sotres distance of last strike
global events_last_energy   # Sotres energy of last strike
global events_last_time     # Sotres datetime of last strike

events_l = [0] * 5 # Stores nubmer of lightning strikes in the past (10m, 30m, 1h, 24h, 30d)
events_d = [0] * 5 # Stores nubmer of disturber events in the past (10m, 30m, 1h, 24h, 30d)
events_n = [0] * 5 # Stores nubmer of noise events in the past (10m, 30m, 1h, 24h, 30d)
events_a = [0] * 5 # Stores nubmer of algo update events in the past (10m, 30m, 1h, 24h, 30d)
events_last_distance = 0 # Stores distance of last strike
events_last_energy = 0 # Stores energy of last strike
events_last_time = 0 # Stores datetime of last strike

global logging
log_path = "/var/log/pi-lightning-detect/pi-l-detect.log"

#
# Logging
#
def log_create():
    format = "%(asctime)s.%(msecs)03d %(levelname)s %(process)d (%(name)s-%(threadName)s) %(message)s (linuxThread-%(thread)d)"
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    log_handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=30)
    log_handler.setFormatter(format)
    logger.addHandler(log_handler)
    #logging.basicConfig(format=format, level=logging.INFO, datefmt="%m/%d/%Y %H:%M:%S")

#
# DB and statistics update functions
#
def db_create():
    global conn
    global c
    global db_lock
    db_lock = threading.Lock()
    db_lock.acquire()
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE ld_lightning (date datetime, distance int, energy int)")
    c.execute("CREATE TABLE ld_disturber (date datetime)")
    c.execute("CREATE TABLE ld_noise (date datetime)")
    c.execute("CREATE TABLE ld_algo (date datetime)")
    conn.commit()
    db_lock.release()
    logging.info('In Memory databases setup')

def detected_lightning(distance, energy):
    global events_last_distance
    global events_last_energy
    global events_last_time
    events_last_time = datetime.now()
    events_last_distance = distance
    events_last_energy = energy
    db_lock.acquire()
    c.execute("INSERT INTO ld_lightning VALUES (?,?,?)", (events_last_time, distance, energy))
    conn.commit()
    db_lock.release()
    logging.info('Lightning - Distance: %sKm, Engery: %s', distance, energy)
    stats_update('lightning')

def detected_disturber():
    db_lock.acquire()
    c.execute("INSERT INTO ld_disturber VALUES (?)", [datetime.now()])
    conn.commit()
    db_lock.release()
    logging.info('Disturber')
    stats_update('disturber')

def detected_noise():
    db_lock.acquire()
    c.execute("INSERT INTO ld_noise VALUES (?)", [datetime.now()])
    conn.commit()
    db_lock.release()
    logging.info('Noise')
    stats_update('noise')

def detected_algo_updated():
    db_lock.acquire()
    c.execute("INSERT INTO ld_algo VALUES (?)", [datetime.now()])
    conn.commit()
    db_lock.release()
    logging.info('Distance algo updated')
    stats_update('algo')

def stats_update(event_type):
    # Update stats variables with data from in memeory DB.
    time_10m = datetime.now() - timedelta(minutes=10)
    time_30m = datetime.now() - timedelta(minutes=30)
    time_1h = datetime.now() - timedelta(hours=1)
    time_24h = datetime.now() - timedelta(hours=24)
    time_30d = datetime.now() - timedelta(days=30)
    db_lock.acquire()
    if event_type == 'lightning':
        c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_10m,))
        events_l[0]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_30m,))
        events_l[1]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_1h,))
        events_l[2]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_24h,))
        events_l[3]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_30d,))
        events_l[4]=c.fetchone()[0]
    elif event_type == 'disturber':
        c.execute("SELECT COUNT(*) FROM ld_disturber WHERE date > ?", (time_10m,))
        events_d[0]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_disturber WHERE date > ?", (time_30m,))
        events_d[1]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_disturber WHERE date > ?", (time_1h,))
        events_d[2]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_disturber WHERE date > ?", (time_24h,))
        events_d[3]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_disturber WHERE date > ?", (time_30d,))
        events_d[4]=c.fetchone()[0]
    elif event_type == 'noise':
        c.execute("SELECT COUNT(*) FROM ld_noise WHERE date > ?", (time_10m,))
        events_n[0]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_noise WHERE date > ?", (time_30m,))
        events_n[1]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_noise WHERE date > ?", (time_1h,))
        events_n[2]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_noise WHERE date > ?", (time_24h,))
        events_n[3]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_noise WHERE date > ?", (time_30d,))
        events_n[4]=c.fetchone()[0]
    elif event_type == 'algo':
        c.execute("SELECT COUNT(*) FROM ld_algo WHERE date > ?", (time_10m,))
        events_a[0]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_algo WHERE date > ?", (time_30m,))
        events_a[1]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_algo WHERE date > ?", (time_1h,))
        events_a[2]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_algo WHERE date > ?", (time_24h,))
        events_a[3]=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM ld_algo WHERE date > ?", (time_30d,))
        events_a[4]=c.fetchone()[0]
    else:
        pass
    db_lock.release()
    #slogging.info('Stats updated for %s', event_type)
    # Update Display not stats have changed
    thread_display = threading.Thread(target=display_stats_update)
    thread_display.start()

    # print(time_10m, time_30m, time_1h, time_24h, time_30d)
    # print(l_strikes_10m, l_strikes_30m, l_strikes_1h, l_strikes_24h, l_strikes_30d)
    # print(events_l)

def db_dump(table_name):
    # table_name can be ld_lightning, ld_disturber, ld_noise, ld_algo
    db_lock.acquire()
    if table_name == 'ld_lightning':
        c.execute("SELECT * FROM ld_lightning")
    elif table_name == 'ld_disturber':
        c.execute("SELECT * FROM ld_disturber")
    elif table_name == 'ld_noise':
        c.execute("SELECT * FROM ld_noise")
    elif table_name == 'ld_algo':
        c.execute("SELECT * FROM ld_algo")
    else:
        pass
    print(c.fetchall())
    db_lock.release()


#
# PiOLED functions
#
def display_init():
    # PiOLED - initialise
    global disp
    global draw
    global image
    global width
    global height
    global top
    global bottom
    global disp_lock
    disp_lock = threading.Lock()
    disp_lock.acquire()
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
    global font_msd_16
    global font_msd_12
    global font_msd_14
    global font_msd_20
    
    font = ImageFont.load_default()
    font_dvs_7 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 7)
    font_dvs_14 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    font_dvs_28 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
    font_msd_8 = ImageFont.truetype('fonts/Museo Sans Display Light.ttf', 8)
    font_msd_12 = ImageFont.truetype('fonts/Museo Sans Display Light.ttf', 12)
    font_msd_14 = ImageFont.truetype('fonts/Museo Sans Display Light.ttf', 14)
    font_msd_16 = ImageFont.truetype('fonts/Museo Sans Display Light.ttf', 16)
    font_msd_20 = ImageFont.truetype('fonts/Museo Sans Display Light.ttf', 20)

    logging.info('Display initialised')
    disp_lock.release()

def display_clear():
    disp_lock.acquire()
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp_lock.release()

def display_stats_update():
    display_clear() # TODO will want to change this to only clear the stats area.
    disp_lock.acquire()
    typeface = font_dvs_14
    if (events_last_time != 0):
        mesg = f'{events_last_distance}Km E {round(events_last_energy, 2)}%'
        draw.text((x, top), mesg, font=typeface, fill=255)
        last_time_diff = datetime.now() - events_last_time
        last_time_diff_sec_total = last_time_diff.seconds
        last_time_diff_mins = (last_time_diff_sec_total//60)
        last_time_diff_sec = (last_time_diff_sec_total - (last_time_diff_mins * 60))
        #logging.info("calculated last time: %sm %ss", last_time_diff_mins, last_time_diff_sec)
        if (last_time_diff_sec_total < 5):
            mesg = " * LIGHTNING *"
        else:
            mesg = f'{last_time_diff_mins}m {last_time_diff_sec}s ago'
        draw.text((x, top+16), mesg, font=typeface, fill=255)
        disp.image(image)
    else:
        mesg = 'Detector started'
        draw.text((x, top), mesg, font=typeface, fill=255)
        mesg = 'wait for lightning'
        draw.text((x, top+16), mesg, font=typeface, fill=255)
        disp.image(image)
    disp.show()
    disp_lock.release()
    #logging.info('Updated display')

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
    disp_lock.acquire()
    draw.text((x, top+offset+y), mesg, font=typeface, fill=255)
    disp.image(image)
    disp.show()
    disp_lock.release()

def disp_get_y(line):
    switcher = {
        1: 0,
        2: 7,
        3: 14,
        4: 21
    }
    return switcher.get(line, 0)

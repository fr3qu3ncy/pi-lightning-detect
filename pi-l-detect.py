# Pi Lightning Detect - Micro Cube Technology
# Control of AS3935 lightning sensor, and stsus updates to PiOLED display

# file pi-l-detect.py

# General imports
from pi_ld_lib import *
#from pi_ld_oled_lib import *
import pi_ld_global

# AS3935 imports
from DFRobot_AS3935_Lib import DFRobot_AS3935
import RPi.GPIO as GPIO

# Set up logging
#log_create()
format = "%(asctime)s.%(msecs)03d %(levelname)s %(process)d (%(name)s-%(threadName)s) %(message)s (linuxThread-%(thread)d)"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%m/%d/%Y %H:%M:%S")

logging.info('pi-lightgning-detect started')
# Create in memeory database
db_create()
# Initialise display
display_init()

# I2C address - AS3935
AS3935_I2C_ADDR1 = 0X01
AS3935_I2C_ADDR2 = 0X02
AS3935_I2C_ADDR3 = 0X03
# Antenna tuning capcitance (must be integer multiple of 8, 8 - 120 pf)
AS3935_CAPACITANCE = 96
# Watchdog Threshold - default value of 0010 / 0x02
AS3935_WDTH = 0x02
# Spike Rejection - default value of 0010 / 0x02
AS3935_SREJ = 0x02
# Minimum Strikes in 15 mins to start alerting - default value 1 - Options are 1, 5, 9 or 16 strikes
AS3935_MIN_SRK = 5
# GPIO Pin
IRQ_PIN = 4

# AS2925 - initialise
sensor = DFRobot_AS3935(AS3935_I2C_ADDR3, bus=1)
if (sensor.reset()):
    logging.info("Initialisation of sensor sucess.")
    disp_text("Init sensor sucess.", 1, 7)
else:
    logging.info("Initialisation sensor fail")
    disp_text("Init sensor fail", 1, 7)
    while True:
        pass
# Configure sensor
sensor.powerUp()
# Set indoors or outdoors models
sensor.setIndoors()
logging.info("Sensor set to indoor mode")
disp_text("Indoor", 2, 7)
#sensor.setOutdoors()
#logging.info("Sensor set to outdoor mode")
#disp_text("Outdoor", 2, 7)

# Disturber detection
#sensor.disturberEn()
#logging.info("Disterbers will be raised and logged")
#disp_text("Disterbers on", 3, 7)
sensor.disturberDis()
logging.info("Disterbers not raised")
disp_text("Disterbers off", 3, 7)

# Watchdog Threshold [WDTH] - Detection efficiency (sensitivity of lightning detection vs disterber rejection) 0x00 to 0x10
sensor.setWatchdogThreshold(AS3935_WDTH)
logging.info(f'Watchdog Threshold: {AS3935_WDTH}')
disp_text(f'WDTH {AS3935_WDTH}', 4, 7)

# Spike Rejection [SREJ] - Detection efficiency (sensitivity of lightning detection vs disterber rejection) 0x00 to 0x10
sensor.setSpikeRejection(AS3935_SREJ)
logging.info(f'Spike Rejection: {AS3935_SREJ}')
disp_text(f'SREJ {AS3935_SREJ}', 1, 7)

# Minumum Strikes in 15 mins.
sensor.setMinStrikes(AS3935_MIN_SRK)
disp_text(f'MIN_SRK {AS3935_MIN_SRK}', 2, 7)

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
#sensor.setWatchdogThreshold(2)
#wtdgThreshold = sensor.getWatchdogThreshold()

#used to modify SREJ (spike rejection),values should only be between 0x00 and 0x0F (0 and 7)
#sensor.setSpikeRejection(2)
#spikeRejection = sensor.getSpikeRejection()

#view all register data
logging.info("Dump of AS2925 Registers")
sensor.printAllRegs()



def callback_handle(channel):
    global sensor
    time.sleep(0.005)
    intSrc = sensor.getInterruptSrc()
    if intSrc == 1:
        lightningDistKm = sensor.getLightningDistKm()
        lightningEnergyVal = sensor.getStrikeEnergyRaw()
        thread_updater = threading.Thread(target=detected_lightning, args=[lightningDistKm, lightningEnergyVal])
        thread_updater.start()
    elif intSrc == 2:
        # disp_text('Disturber discovered', 2, 7)
        thread_updater = threading.Thread(target=detected_disturber)
        thread_updater.start()
    elif intSrc == 3:
        # disp_text('Noise level too high', 2, 7)
        thread_updater = threading.Thread(target=detected_noise)
        thread_updater.start()
    else:
        # disp_text('Distance algo updated', 2, 7)
        thread_updater = threading.Thread(target=detected_algo_updated)
        thread_updater.start()
        pass

# pylint: disable=no-member
# Set IRQ pin to input mode
GPIO.setup(IRQ_PIN, GPIO.IN)
# Set the interrupt pin, the interrupt function, rising along the trigger
GPIO.add_event_detect(IRQ_PIN, GPIO.RISING, callback = callback_handle)
# pylint: enable=no-member

logging.info("Detection started...")
disp_text("Detection started", 2, 7)

#TEST CODE
# time.sleep(1.5)
# display_stats_update()
# time.sleep(5.5)
# thread_updater = threading.Thread(target=detected_lightning, args=[31, 11.0000])
# thread_updater.start()
# logging.info("Started thread : %s", thread_updater.name)
# thread_updater = threading.Thread(target=detected_disturber)
# thread_updater.start()
# thread_updater = threading.Thread(target=detected_noise)
# thread_updater.start()
# thread_updater = threading.Thread(target=detected_algo_updated)
# thread_updater.start()
# time.sleep(2)
# thread_updater = threading.Thread(target=detected_lightning, args=[27, 2.5234])
# thread_updater.start()
# time.sleep(4)
# thread_updater = threading.Thread(target=detected_lightning, args=[14, 22.88921])
# thread_updater.start()
# time.sleep(4)
# thread_updater = threading.Thread(target=detected_lightning, args=[12, 31.63242])
# thread_updater.start()
# time.sleep(0.5)
logging.info("Dump of Database")
db_dump('ld_lightning')
db_dump('ld_disturber')
db_dump('ld_noise')
db_dump('ld_algo')
# display_stats_update()
# stats_update()

while True:
    time.sleep(1.0)
    try:
        display_stats_update()
    except IOError as e:
        error = e
        logging.error("Error updating OLED diaply: %s", error)
        display_init()


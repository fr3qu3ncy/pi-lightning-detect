# Pi Lightning Detect - Micro Cube Technology
# Functions for pi-l-detect

# file pi_ld_lib.py

import sys
import time
from datetime import datetime, timedelta
import logging
import threading
import sqlite3

global l_events        # Stores nubmer of lightning strikes in the past (10m, 30m, 1h, 24h, 30d)
l_events = [0] * 5
global d_events        # Stores nubmer of disturber events in the past (10m, 30m, 1h, 24h, 30d)
d_events = [0] * 5
global n_events        # Stores nubmer of noise events in the past (10m, 30m, 1h, 24h, 30d)
n_events = [0] * 5
global a_events        # Stores nubmer of algo update events in the past (10m, 30m, 1h, 24h, 30d)
a_events = [0] * 5

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
    db_lock.acquire()
    c.execute("INSERT INTO ld_lightning VALUES (?,?,?)", (datetime.now(), distance, energy))
    conn.commit()
    db_lock.release()
    logging.info('Lightning - Distance: %sKm, Engery: %s', distance, energy)

def detected_disturber():
    db_lock.acquire()
    c.execute("INSERT INTO ld_disturber VALUES (?)", [datetime.now()])
    conn.commit()
    db_lock.release()
    logging.info('Disturber')

def detected_noise():
    db_lock.acquire()
    c.execute("INSERT INTO ld_noise VALUES (?)", [datetime.now()])
    conn.commit()
    db_lock.release()
    logging.info('Noise')
    time.sleep(2)

def detected_algo_updated():
    db_lock.acquire()
    c.execute("INSERT INTO ld_algo VALUES (?)", [datetime.now()])
    conn.commit()
    db_lock.release()
    logging.info('Distance algo updated')

def stats_update():
    # Update stats variables with data from in memeory DB.
    time_10m = datetime.now() - timedelta(minutes=10)
    time_30m = datetime.now() - timedelta(minutes=30)
    time_1h = datetime.now() - timedelta(hours=1)
    time_24h = datetime.now() - timedelta(hours=24)
    time_30d = datetime.now() - timedelta(days=30)
    db_lock.acquire()
    c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_10m,))
    l_events[0]=c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_30m,))
    l_events[1]=c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_1h,))
    l_events[2]=c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_24h,))
    l_events[3]=c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ld_lightning WHERE date > ?", (time_30d,))
    l_events[4]=c.fetchone()[0]
    db_lock.release()
    # print(time_10m, time_30m, time_1h, time_24h, time_30d)
    # print(l_strikes_10m, l_strikes_30m, l_strikes_1h, l_strikes_24h, l_strikes_30d)
    print(l_events)

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
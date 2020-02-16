# Pi Lightning Detect - Micro Cube Technology
# Functions for pi-l-detect

# file pi-ld-lib.py

import sys
import time
from datetime import datetime
import logging
import threading
import sqlite3


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
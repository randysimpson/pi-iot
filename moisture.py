'''
Copyright (©) 2021 - Randall Simpson
pi-iot

This class is used to gather moisture sensor metrics from a raspberry pi.

Psudocode:
If the value changes from the initial value then lets record the changes for the delay duration
and return an average value on a per minute basis.  If the value stays the same then no reporting necessary.
'''
from sensor import Sensor
from generic import Generic
from metric import Metric
import datetime
import sys
import RPi.GPIO as GPIO
import time
import logging

logger = logging.getLogger('root')

class Moisture(Generic):
    def __init__(self, source, metric_prefix, output, code, pin, metric_name, delay):
        Generic.__init__(self, source, metric_prefix, output, code, pin, metric_name)
        self.delay = delay
        self.data = []

    def get_info(self):
        current_value = GPIO.input(self.pin)
        last_change_time = time.time()
        while current_value == self.initial_value:
            #do nothing, wait for a change
            current_value = GPIO.input(self.pin)
            time.sleep(0.00001)
            if len(self.data) > 0 and time.time() - last_change_time > self.delay:
                val = len(self.data) / 1500
                if current_value == 1:
                    val = 1.0 - val
                logger.debug(f'val: {val}, length: {len(self.data)}')
                self.metrics.append(Metric(self.name, val, datetime.datetime.utcnow()))
                #reset past readings and set initial value so if it's at 0.5 it can be corrected to 0 or 1
                self.data = []
                self.initial_value = val
        # changed
        self.data.append(current_value)
        current_time = time.time()
        if current_time - last_change_time > self.delay:
            #send metric
            val = len(self.data) / 1500
            if current_value == 1:
                val = 1.0 - val
            logger.debug(f'val: {val}, length: {len(self.data)}')
            self.metrics.append(Metric(self.name, val, datetime.datetime.utcnow()))
            #reset time/past readings
            last_change_time = current_time
            self.data = []
        self.initial_value = current_value

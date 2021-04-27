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

    def get_info(self):
        last_change_time = time.time()
        current_time = time.time()
        change_count = 0

        while current_time - last_change_time < self.delay:
            #loop during time to see if any changes happen
            current_value = GPIO.input(self.pin)
            time.sleep(0.00001)
            current_time = time.time()

            if current_value != self.initial_value:
                change_count += 1
                self.initial_value = current_value

        #delay time is up, send metric if necessary
        if change_count > 0:
            #send a value of 0.5 if there is flapping, otherwise send the current value
            val = 0.5 if change_count > 1 else current_value
            self.metrics.append(Metric(self.name, val, datetime.datetime.utcnow()))

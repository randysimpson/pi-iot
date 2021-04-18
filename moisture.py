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
        self.has_changed = False

    def get_info(self):
        current_value = GPIO.input(self.pin)
        last_change_time = time.time()
        current_time = time.time()
        while current_value == self.initial_value:
            #do nothing, wait for a change
            current_value = GPIO.input(self.pin)
            time.sleep(0.00001)
            current_time = time.time()
            # this case is when the flapping stops inbetween delay
            if self.has_changed and current_time - last_change_time > self.delay + 1:
                self.metrics.append(Metric(self.name, 0.5, datetime.datetime.utcnow()))
                #reset past readings and set initial value so if it's at 0.5 it can be corrected to 0 or 1
                self.has_changed = False
                self.initial_value = 0.5
                #set a delay to buffer then end result value
                time.sleep(self.delay)
        # value changed
        if current_time - last_change_time > self.delay:
            #send metric
            val = 0.5 if self.has_changed else current_value
            self.metrics.append(Metric(self.name, val, datetime.datetime.utcnow()))
            #reset time/past readings
            last_change_time = current_time
            self.has_changed = False
        else:
            self.has_changed = True
        self.initial_value = current_value

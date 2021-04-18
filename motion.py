'''
Copyright (©) 2020 - Randall Simpson
pi-iot

This class is used to gather motion sensor metrics from a raspberry pi.
'''
from sensor import Sensor
from metric import Metric
import datetime
import sys
import RPi.GPIO as GPIO
import time
import logging

logger = logging.getLogger('root')

class Motion(Sensor):
    def __init__(self, source, metric_prefix, output, code, pin):
        Sensor.__init__(self, source, metric_prefix, output)

        self.pin = pin
        self.tag_label = code
        self.name = self.metric_prefix + 'motion'
        if self.output == 'WF':
            self.name = 'Motion'
            if len(self.metric_prefix) > 0:
                self.name = self.metric_prefix + '.' + self.name
        self.initPins()

    def __del__(self):
        #destructor to clean up Pins.
        GPIO.cleanup()

    def initPins(self):
        #init pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN)

        #allow pin to initialize
        logger.debug("Initializing...")
        time.sleep(60)

        #find initial pin value
        self.initial_value = GPIO.input(self.pin)
        self.last_change_time = time.time()
        self.in_motion = False
        logger.debug("Ready")

    def reset(self):
        #clean up first
        try:
            GPIO.cleanup()
        finally:
            self.initPins()

    def get_info(self):
        current_value = GPIO.input(self.pin)
        while current_value == self.initial_value:
            #do nothing, wait for a change
            current_value = GPIO.input(self.pin)
            time.sleep(0.00001)
            pulse_end_time = time.time()
            if self.in_motion is False and current_value == 1 and pulse_end_time - self.last_change_time > 3.7:
                self.metrics.append(Metric(self.name, 1.0, datetime.datetime.utcnow()))
                self.in_motion = True
        # changed
        self.initial_value = current_value
        self.last_change_time = time.time()
        if current_value == 0 and self.in_motion is True:
            self.metrics.append(Metric(self.name, 0.0, datetime.datetime.utcnow()))
            self.in_motion = False

    def format_metrics(self):
        rtnMetrics = []
        while len(self.metrics) > 0:
            metric = self.metrics.pop()
            if self.output == 'WF':
                tags = {}
                tags['Pin'] = self.pin
                tags['Sensor'] = self.tag_label
                detail = {}
                detail['value'] = metric.value
                detail['tags'] = tags
                m = {}
                m[metric.name] = detail
                rtnMetrics.append(m)
            else:
                m = {}
                m['date'] = metric.date.isoformat() + 'Z'
                m['metric'] = metric.name
                m['value'] = metric.value
                m['source'] = self.source
                tags = {}
                tags['pin'] = self.pin
                tags['sensor'] = self.tag_label
                m['tags'] = tags
                rtnMetrics.append(m)
        return rtnMetrics

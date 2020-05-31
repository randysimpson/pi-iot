'''
Copyright (©) 2020 - Randall Simpson
pi-iot

This class is used to gather generic sensor metrics from a raspberry pi.
'''
from sensor import Sensor
from metric import Metric
import datetime
import sys
import RPi.GPIO as GPIO
import time

class Generic(Sensor):
    def __init__(self, source, metric_prefix, output, code, pin, metric_name):
        Sensor.__init__(self, source, metric_prefix, output)

        self.pin = pin
        self.tag_label = code
        self.name = self.metric_prefix + metric_name.lower()
        if self.output == 'WF':
            self.name = metric_name
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
        time.sleep(2)

        #find initial pin value
        self.initial_value = GPIO.input(self.pin)

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
        # changed
        self.initial_value = current_value
        self.metrics.append(Metric(self.name, current_value, datetime.datetime.utcnow()))

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
